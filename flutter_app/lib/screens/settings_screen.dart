import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  static const routeName = '/settings';
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _numeController = TextEditingController();
  final _prenumeController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _plateController = TextEditingController();
  final ApiService _apiService = ApiService();

  bool _loading = true;
  bool _saving = false;
  String? _token;

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) return 'Email-ul este obligatoriu';
    final emailRegex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+');
    if (!emailRegex.hasMatch(value)) return 'Email invalid';
    return null;
  }

  String? _validateOptionalPassword(String? value) {
    if (value != null && value.isNotEmpty && value.length < 6) {
      return 'Parola trebuie să aibă cel puțin 6 caractere';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    final password = _passwordController.text.trim();
    if (password.isEmpty) return null;
    if (value == null || value.isEmpty) return 'Parola de confirmare este obligatorie';
    if (value != password) return 'Parolele nu se potrivesc';
    return null;
  }

  String? _validateRequired(String? value, String field) {
    if (value == null || value.isEmpty) return '$field este obligatoriu';
    return null;
  }

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('jwt_token');
      if (!mounted) return;

      if (token == null || token.isEmpty) {
        setState(() {
          _loading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Autentificăți-vă din nou')),
        );
        return;
      }

      _token = token;
      final response = await _apiService.getProfile(token);
      if (!mounted) return;

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        _numeController.text = body['nume']?.toString() ?? '';
        _prenumeController.text = body['prenume']?.toString() ?? '';
        _emailController.text = body['email']?.toString() ?? '';
        _plateController.text = body['numar_inmatriculare']?.toString() ?? '';
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Profilul nu a putut fi încarcat (${response.statusCode})')),
        );
      }
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Eroare la încărcarea profilului: $error')),
      );
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;
    if (_token == null || _token!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Token de autentificare lipsă')),
      );
      return;
    }

    setState(() => _saving = true);
    final payload = <String, dynamic>{
      'nume': _numeController.text.trim(),
      'prenume': _prenumeController.text.trim(),
      'email': _emailController.text.trim(),
      'numar_inmatriculare': _plateController.text.trim(),
    };
    if (_passwordController.text.trim().isNotEmpty) {
      payload['password'] = _passwordController.text;
    }

    try {
      final response = await _apiService.updateProfile(_token!, payload);
      if (!mounted) return;

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profilul a fost actualizat cu succes')),
        );
        _passwordController.clear();
      } else {
        String message = 'Nu s-a putut actualiza profilul';
        try {
          final body = jsonDecode(response.body);
          if (body is Map<String, dynamic> && body['detail'] != null) {
            message = body['detail'].toString();
          }
        } catch (_) {}
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Eroare la salvarea profilului: $error')),
      );
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  @override
  void dispose() {
    _numeController.dispose();
    _prenumeController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _plateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Setări Cont')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Icon(
                      Icons.account_circle_rounded,
                      size: 80,
                      color: Color(0xFF2563EB),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Editează profilul',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 32),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _numeController,
                            decoration: const InputDecoration(labelText: 'Nume'),
                            validator: (value) => _validateRequired(value, 'Nume'),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: TextFormField(
                            controller: _prenumeController,
                            decoration: const InputDecoration(labelText: 'Prenume'),
                            validator: (value) => _validateRequired(value, 'Prenume'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email',
                        prefixIcon: Icon(Icons.email_outlined),
                      ),
                      validator: _validateEmail,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _passwordController,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Parolă (opțional)',
                        prefixIcon: Icon(Icons.lock_outline),
                      ),
                      validator: _validateOptionalPassword,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _confirmPasswordController,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Confirmă parola',
                        prefixIcon: Icon(Icons.lock_reset_outlined),
                      ),
                      validator: _validateConfirmPassword,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _plateController,
                      decoration: const InputDecoration(
                        labelText: 'Număr înmatriculare',
                        prefixIcon: Icon(Icons.directions_car_outlined),
                      ),
                      textCapitalization: TextCapitalization.characters,
                      inputFormatters: [UpperCaseTextFormatter()],
                      validator: (value) => _validateRequired(value, 'Număr înmatriculare'),
                    ),
                    const SizedBox(height: 48),
                    SizedBox(
                      height: 56,
                      child: _saving
                          ? const Center(child: CircularProgressIndicator())
                          : FilledButton(
                              onPressed: _saveProfile,
                              child: const Text('Salvează modificările', style: TextStyle(fontSize: 18)),
                            ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}

class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(TextEditingValue oldValue, TextEditingValue newValue) {
    return TextEditingValue(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
      composing: TextRange.empty,
    );
  }
}
