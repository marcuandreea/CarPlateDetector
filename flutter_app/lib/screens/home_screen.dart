import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  static const routeName = '/home';
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Home')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        const Text('Home Screen', style: TextStyle(fontSize: 20)),
        const SizedBox(height: 16),
        ElevatedButton(
          onPressed: () => Navigator.pushNamed(context, '/qr'),
          child: const Text('Show QR'),
        ),
        const SizedBox(height: 8),
        ElevatedButton(
          onPressed: () => Navigator.pushNamed(context, '/subscription'),
          child: const Text('Subscription'),
        ),
        const SizedBox(height: 8),
        ElevatedButton.icon(
          onPressed: () => Navigator.pushNamed(
            context,
            '/payment-details',
          ),
          icon: const Icon(Icons.credit_card),
          label: const Text('Plată parcare'),
        ),
        const SizedBox(height: 8),
        ElevatedButton(
          onPressed: () => Navigator.pushNamed(context, '/settings'),
          child: const Text('Settings'),
        ),
      ]),
    );
  }
}
