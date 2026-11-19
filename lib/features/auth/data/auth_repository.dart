import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';

import '../../../core/config/env.dart';
import '../../../core/network/api_client.dart';
import '../domain/user.dart';

/// Resultado del login: el admin entra directo, el cliente necesita OTP.
sealed class LoginResult {}

class LoginSuccess extends LoginResult {
  LoginSuccess(this.token, this.user);
  final String token;
  final User user;
}

class LoginNeedsOtp extends LoginResult {
  LoginNeedsOtp({required this.email, required this.message, this.otpDev});
  final String email;
  final String message;

  /// Solo llega en desarrollo cuando el backend no pudo enviar el correo.
  final String? otpDev;
}

class RegisterData {
  const RegisterData({
    required this.nombre,
    required this.email,
    required this.password,
    required this.edad,
    this.username,
    this.telefono,
  });

  final String nombre;
  final String email;
  final String password;
  final int edad;
  final String? username;
  final String? telefono;

  Map<String, dynamic> toJson() => {
        'nombre': nombre.trim(),
        'email': email.trim().toLowerCase(),
        'password': password,
        'edad': edad,
        if (username != null && username!.trim().isNotEmpty) 'username': username!.trim(),
        if (telefono != null && telefono!.trim().isNotEmpty) 'telefono': telefono!.trim(),
      };
}

const esquemaRegresoGoogle = 'skonditbeats';

const _erroresGoogle = {
  'google_cancelled': 'Cancelaste el inicio de sesión con Google.',
  'google_no_email': 'Tu cuenta de Google no compartió el correo.',
  'google_create_failed': 'No se pudo crear tu cuenta. Intenta de nuevo.',
  'account_disabled': 'Tu cuenta está desactivada.',
  'google_otp_failed': 'No pudimos enviarte el código de verificación. Intenta de nuevo.',
  'google_failed': 'No se pudo iniciar sesión con Google. Intenta de nuevo.',
};

/// Interpreta skonditbeats://login?google=1&email=…[&otpDev=…] o ?error=…
/// Google ya confirmó la identidad; falta el código OTP que llega al correo.
LoginNeedsOtp leerRegresoGoogle(Uri uri) {
  final q = uri.queryParameters;
  final error = q['error'];
  if (error != null) {
    throw ApiException(_erroresGoogle[error] ?? _erroresGoogle['google_failed']!);
  }
  final email = q['email'];
  if (uri.scheme != esquemaRegresoGoogle || email == null || email.isEmpty) {
    throw ApiException(_erroresGoogle['google_failed']!);
  }
  return LoginNeedsOtp(
    email: email,
    message: 'Te enviamos un código de verificación a tu correo',
    otpDev: q['otpDev'],
  );
}

/// Endpoints de /api/auth (mismos que consume la web).
class AuthRepository {
  AuthRepository(this._dio);

  final Dio _dio;

  Future<LoginResult> login(String email, String password) async {
    final data = await _post('/auth/login', {
      'email': email.trim().toLowerCase(),
      'password': password,
    });

    if (data['requires2fa'] == true) {
      final email = data['email'];
      if (email is! String || email.isEmpty) throw ApiException(respuestaInvalida);
      return LoginNeedsOtp(
        email: email,
        message: (data['message'] as String?) ?? 'Código enviado a tu correo',
        otpDev: data['otpDev'] as String?,
      );
    }
    return _sesion(data);
  }

  Future<LoginSuccess> verifyOtp(String email, String code) async {
    final data = await _post('/auth/verify-otp', {'email': email, 'code': code});
    return _sesion(data);
  }

  Future<LoginSuccess> register(RegisterData body) async {
    final data = await _post('/auth/register', body.toJson());
    return _sesion(data);
  }

  /// Inicio de sesión con Google en el navegador del sistema. La API hace el OAuth
  /// igual que en la web y al final regresa a la app con skonditbeats://login?...
  /// Devuelve null si el usuario cerró el navegador sin terminar.
  Future<LoginNeedsOtp?> loginConGoogle() async {
    final String regreso;
    try {
      regreso = await FlutterWebAuth2.authenticate(
        url: '${Env.apiUrl}/auth/google?app=movil',
        callbackUrlScheme: esquemaRegresoGoogle,
      );
    } on PlatformException catch (e) {
      if (e.code == 'CANCELED') return null;
      throw ApiException('No se pudo abrir el inicio de sesión con Google.');
    }
    return leerRegresoGoogle(Uri.parse(regreso));
  }

  /// Registra el cierre de sesión en la bitácora. Si falla no importa.
  Future<void> logout() async {
    try {
      await _dio.post('/auth/logout', data: {});
    } catch (_) {}
  }

  /// Mensaje cuando la API contesta 200 pero sin lo que la app necesita.
  static const respuestaInvalida = 'La respuesta del servidor no es válida. Intenta de nuevo.';

  /// Convierte {token, user} en una sesión. Antes se hacía `data['token'] as String`
  /// y una respuesta incompleta (proxy, caché, versión vieja de la API) lanzaba un
  /// TypeError que la pantalla no atrapaba: el botón volvía a la normalidad sin
  /// ningún mensaje (Prácticas 13 y 14, AUT-04g / AUT-05d).
  static LoginSuccess _sesion(Map<String, dynamic> data) {
    final token = data['token'];
    final user = data['user'];
    if (token is! String || token.isEmpty || user is! Map<String, dynamic> ||
        user['id'] is! String || user['email'] is! String) {
      throw ApiException(respuestaInvalida);
    }
    return LoginSuccess(token, User.fromJson(user));
  }

  Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> body) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(path, data: body);
      return res.data ?? {};
    } on DioException catch (e) {
      throw ApiException.fromDio(e);
    }
  }
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(dioProvider));
});
