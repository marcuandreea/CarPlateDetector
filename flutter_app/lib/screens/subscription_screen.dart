import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/subscription_plan.dart';
import '../models/active_subscription.dart';
import '../services/api_service.dart';
import 'card_payment_screen.dart';

class _SubscriptionData {
  final List<SubscriptionPlan> plans;
  final ActiveSubscription? activeSubscription;

  _SubscriptionData(this.plans, this.activeSubscription);
}

class SubscriptionScreen extends StatefulWidget {
  static const routeName = '/subscription';
  const SubscriptionScreen({super.key});

  @override
  State<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends State<SubscriptionScreen> {
  final ApiService _apiService = ApiService();
  late Future<_SubscriptionData> _dataFuture;

  @override
  void initState() {
    super.initState();
    _dataFuture = _fetchData();
  }

  Future<_SubscriptionData> _fetchData() async {
    final plans = await _apiService.getSubscriptionPlans();
    ActiveSubscription? activeSub;
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');
    if (token != null && token.isNotEmpty) {
      activeSub = await _apiService.getActiveSubscription(token);
    }
    return _SubscriptionData(plans, activeSub);
  }

  void _selectPlan(SubscriptionPlan plan, bool hasActiveSubscription) {
    if (hasActiveSubscription) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ai deja un abonament activ. Nu poți achiziționa altul.')),
      );
      return;
    }
    
    Navigator.pushNamed(
      context,
      CardPaymentScreen.routeName,
      arguments: plan,
    ).then((value) {
      // Re-fetch data when returning from payment screen
      setState(() {
        _dataFuture = _fetchData();
      });
    });
  }

  String _formatDate(DateTime date) {
    final day = date.day.toString().padLeft(2, '0');
    final month = date.month.toString().padLeft(2, '0');
    final year = date.year;
    final hour = date.hour.toString().padLeft(2, '0');
    final minute = date.minute.toString().padLeft(2, '0');
    return '$day.$month.$year $hour:$minute';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Abonamente')),
      body: FutureBuilder<_SubscriptionData>(
        future: _dataFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Eroare la încărcarea abonamentelor: ${snapshot.error}'),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _dataFuture = _fetchData();
                      });
                    },
                    child: const Text('Reîncearcă'),
                  ),
                ],
              ),
            );
          }

          final data = snapshot.data;
          if (data == null) {
            return const Center(child: Text('Nu s-au putut prelua datele.'));
          }

          final plans = data.plans;
          final activeSub = data.activeSubscription;

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (activeSub != null) ...[
                Card(
                  color: Colors.green.shade50,
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.check_circle, color: Colors.green),
                            const SizedBox(width: 8),
                            Text(
                              'Abonament Activ',
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                color: Colors.green.shade800,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text('Plan: ${activeSub.planNume}', style: const TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text('Expiră la: ${_formatDate(activeSub.endDate)}'),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Nu poți achiziționa un alt abonament cât timp ai unul activ.',
                  style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
                ),
                const SizedBox(height: 16),
              ],
              
              if (plans.isEmpty)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Text('Nu există planuri de abonament în baza de date.'),
                  ),
                )
              else
                ...plans.map((plan) => Card(
                  elevation: activeSub != null ? 0 : 2,
                  color: activeSub != null ? Colors.grey.shade200 : null,
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    title: Text(
                      plan.nume,
                      style: TextStyle(
                        color: activeSub != null ? Colors.grey.shade600 : null,
                      ),
                    ),
                    subtitle: Text(
                      '${plan.price.toStringAsFixed(2)} RON • ${plan.duration} zile',
                      style: TextStyle(
                        color: activeSub != null ? Colors.grey.shade500 : null,
                      ),
                    ),
                    trailing: Icon(
                      Icons.arrow_forward_ios, 
                      size: 16,
                      color: activeSub != null ? Colors.grey.shade400 : null,
                    ),
                    onTap: () => _selectPlan(plan, activeSub != null),
                  ),
                )),
            ],
          );
        },
      ),
    );
  }
}
