/// Formato de precios: 1000 → "$1,000 MXN"; -500 → "-$500 MXN".
///
/// Prácticas 13 y 14 (AUT-03): antes un negativo salía "$-,500 MXN" (el signo contaba
/// como dígito al poner comas) y NaN/Infinity lanzaban UnsupportedError en round().
String formatMoney(num value, {bool currency = true}) {
  final v = value.isFinite ? value : 0;
  final entero = v.round().abs().toString();
  final buf = StringBuffer();
  for (var i = 0; i < entero.length; i++) {
    if (i > 0 && (entero.length - i) % 3 == 0) buf.write(',');
    buf.write(entero[i]);
  }
  final signo = v.round() < 0 ? '-' : '';
  return '$signo\$$buf${currency ? ' MXN' : ''}';
}

/// La API puede mandar números como texto ("300") o como número (300).
/// Lo que no sea un número finito ("NaN", "Infinity", basura) cuenta como 0.
num parseNum(Object? v) {
  final n = v is num ? v : num.tryParse('${v ?? ''}');
  return (n == null || !n.isFinite) ? 0 : n;
}
