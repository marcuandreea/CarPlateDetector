import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/home_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/qr_screen.dart';
import 'screens/subscription_screen.dart';
import 'screens/card_payment_screen.dart';

void main() {
  runApp(const ParkingApp());
}

class ParkingApp extends StatelessWidget {
  const ParkingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Parking App',
      theme: ThemeData(primarySwatch: Colors.blue),
      initialRoute: LoginScreen.routeName,
      routes: {
        LoginScreen.routeName: (_) => const LoginScreen(),
        RegisterScreen.routeName: (_) => const RegisterScreen(),
        HomeScreen.routeName: (_) => const HomeScreen(),
        SettingsScreen.routeName: (_) => const SettingsScreen(),
        QRScreen.routeName: (_) => const QRScreen(),
        SubscriptionScreen.routeName: (_) => const SubscriptionScreen(),
        CardPaymentScreen.routeName: (_) => const CardPaymentScreen(),
      },
    );
  }
}
