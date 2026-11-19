// Prácticas 13 y 14 · Lee el reporte JSON de `flutter test --file-reporter json:<archivo>`
// y escribe un resumen en Markdown: aprobadas, fallidas, omitidas, tiempo y detalle por
// archivo y por código AUT. En GitHub Actions se manda a $GITHUB_STEP_SUMMARY.
//
//   dart run tool/p13/resumen_pruebas.dart reporte.json [salida.md]
import 'dart:convert';
import 'dart:io';

void main(List<String> args) {
  if (args.isEmpty) {
    stderr.writeln('Uso: dart run tool/p13/resumen_pruebas.dart reporte.json [salida.md]');
    exit(64);
  }

  final suites = <int, String>{};
  final pruebas = <int, ({String nombre, int suite, int inicio})>{};
  final resultados = <int, ({String resultado, int fin, bool oculta})>{};
  final errores = <int, List<String>>{};
  var tiempoTotal = 0;

  for (final linea in File(args[0]).readAsLinesSync()) {
    if (linea.trim().isEmpty) continue;
    final e = jsonDecode(linea) as Map<String, dynamic>;
    switch (e['type']) {
      case 'suite':
        final s = e['suite'] as Map<String, dynamic>;
        suites[s['id'] as int] = (s['path'] as String? ?? '?').replaceAll('\\', '/');
      case 'testStart':
        final t = e['test'] as Map<String, dynamic>;
        pruebas[t['id'] as int] = (nombre: t['name'] as String, suite: t['suiteID'] as int, inicio: e['time'] as int);
      case 'testDone':
        final resultado = e['skipped'] == true ? 'skipped' : e['result'] as String;
        resultados[e['testID'] as int] = (resultado: resultado, fin: e['time'] as int, oculta: e['hidden'] == true);
      case 'error':
        errores.putIfAbsent(e['testID'] as int, () => []).add('${e['error']}');
      // En las pruebas de widgets la causa sale como texto impreso ("The following
      // TestFailure was thrown…") y el error es solo "Test failed. See exception logs above."
      case 'print':
        final m = '${e['message']}';
        final causa = RegExp(r'^(No apareció.*|Expected:.*)$', multiLine: true).firstMatch(m);
        if (causa != null) errores.putIfAbsent(e['testID'] as int, () => []).insert(0, causa[0]!);
      case 'done':
        tiempoTotal = e['time'] as int;
    }
  }

  // Los "loading <archivo>" son pruebas ocultas: no se cuentan.
  final visibles = resultados.entries.where((r) => !r.value.oculta).toList();
  int cuenta(bool Function(String r) f) => visibles.where((r) => f(r.value.resultado)).length;
  final aprobadas = cuenta((r) => r == 'success');
  final fallidas = cuenta((r) => r == 'failure' || r == 'error');
  final omitidas = cuenta((r) => r == 'skipped');

  final porArchivo = <String, List<int>>{};
  for (final r in visibles) {
    final p = pruebas[r.key]!;
    final archivo = suites[p.suite]!.split('/test/').last;
    final fila = porArchivo.putIfAbsent(archivo, () => [0, 0, 0, 0]);
    fila[r.value.resultado == 'success' ? 0 : r.value.resultado == 'skipped' ? 2 : 1]++;
    fila[3] += r.value.fin - p.inicio;
  }

  final porAut = <String, List<int>>{};
  for (final r in visibles) {
    final m = RegExp(r'AUT-0\d').firstMatch(pruebas[r.key]!.nombre);
    if (m == null) continue;
    final fila = porAut.putIfAbsent(m[0]!, () => [0, 0]);
    fila[r.value.resultado == 'success' ? 0 : 1]++;
  }

  final md = StringBuffer()
    ..writeln('## Resultado de las pruebas · SkonditBeats Mobile')
    ..writeln()
    ..writeln(fallidas == 0 ? '**✅ Todas las pruebas pasaron.**' : '**❌ $fallidas prueba(s) fallaron.**')
    ..writeln()
    ..writeln('| Ejecutadas | Aprobadas | Fallidas | Omitidas | Tiempo total |')
    ..writeln('|---:|---:|---:|---:|---:|')
    ..writeln('| ${visibles.length} | $aprobadas | $fallidas | $omitidas | ${(tiempoTotal / 1000).toStringAsFixed(1)} s |')
    ..writeln();

  if (porAut.isNotEmpty) {
    md
      ..writeln('### Matriz de automatización')
      ..writeln()
      ..writeln('| Código | Aprobadas | Fallidas |')
      ..writeln('|---|---:|---:|');
    for (final k in porAut.keys.toList()..sort()) {
      md.writeln('| $k | ${porAut[k]![0]} | ${porAut[k]![1]} |');
    }
    md.writeln();
  }

  md
    ..writeln('### Por archivo')
    ..writeln()
    ..writeln('| Archivo | Aprobadas | Fallidas | Omitidas | Tiempo |')
    ..writeln('|---|---:|---:|---:|---:|');
  for (final k in porArchivo.keys.toList()..sort()) {
    final f = porArchivo[k]!;
    md.writeln('| `$k` | ${f[0]} | ${f[1]} | ${f[2]} | ${(f[3] / 1000).toStringAsFixed(1)} s |');
  }

  // Mensaje útil de una falla: el primer error que no sea el genérico "Test failed…",
  // con sus primeras líneas (Expected / Actual / Which).
  String detalle(int id) {
    final lista = errores[id] ?? const [];
    final e = lista.firstWhere((x) => !x.startsWith('Test failed'), orElse: () => lista.isEmpty ? '(sin detalle)' : lista.first);
    final lineas = e.split('\n').map((l) => l.trim()).where((l) => l.isNotEmpty).take(3).join(' | ');
    return lineas.length > 300 ? '${lineas.substring(0, 300)}…' : lineas;
  }

  final conFalla = visibles.where((r) => r.value.resultado != 'success' && r.value.resultado != 'skipped');
  if (conFalla.isNotEmpty) {
    md
      ..writeln()
      ..writeln('### Pruebas fallidas')
      ..writeln();
    for (final r in conFalla) {
      md.writeln('- **${pruebas[r.key]!.nombre}**: ${detalle(r.key)}');
    }
  }

  if (args.length > 1) {
    File(args[1]).writeAsStringSync(md.toString());
  } else {
    stdout.write(md);
  }

  // En GitHub Actions, además, anotaciones: aparecen en la página pública de la corrida
  // (el resumen y los logs solo se ven con sesión iniciada).
  if (Platform.environment['GITHUB_ACTIONS'] == 'true') {
    String limpio(String s) => s.replaceAll('%', '%25').replaceAll('\r', '').replaceAll('\n', ' ');
    stdout.writeln('::notice title=Pruebas: ${visibles.length} ejecutadas::'
        '$aprobadas aprobadas, $fallidas fallidas, $omitidas omitidas en ${(tiempoTotal / 1000).toStringAsFixed(1)} s');
    for (final r in conFalla) {
      final p = pruebas[r.key]!;
      final archivo = 'test/${suites[p.suite]!.split('/test/').last}';
      stdout.writeln('::error file=$archivo,title=${limpio(p.nombre).replaceAll(',', ';').replaceAll('::', ':')}::'
          '${limpio(detalle(r.key))}');
    }
  }
}
