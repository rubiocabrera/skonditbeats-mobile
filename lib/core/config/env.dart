/// Configuración por ambiente. Se inyecta en compilación con --dart-define.
///
/// Sin --dart-define la app usa la API de producción (Vercel, la misma de la
/// web): un APK compilado así funciona solo, con datos o Wi-Fi, sin la PC.
/// Para desarrollar contra la API de la PC:
///   emulador: flutter run --dart-define=API_URL=http://10.0.2.2:3000/api
///   celular:  run_cel.bat  (adb reverse + API_URL=http://127.0.0.1:3000/api)
class Env {
  Env._();

  /// URL base de la API de SkonditBeats (la misma que usa la web).
  static const String apiUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: produccion,
  );

  static const String produccion = 'https://skonditbeats-backend.vercel.app/api';

  /// Con hasta 2 reintentos automáticos, un servidor que no responde se
  /// reporta al usuario en unos 25 s como máximo.
  static const Duration connectTimeout = Duration(seconds: 8);
  static const Duration receiveTimeout = Duration(seconds: 20);
}
