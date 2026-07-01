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
        const SnackBar(
            content:
                Text('Ai deja un abonament activ. Nu poți achiziționa altul.')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CardPaymentScreen.subscription(plan: plan),
      ),
    ).then((value) {
      if (!mounted) return;
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
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline, size: 64, color: Color(0xFFEF4444)),
                    const SizedBox(height: 16),
                    Text(
                      'Eroare la încărcare:\n${snapshot.error}'.replaceFirst('Exception: ', ''),
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Color(0xFF1E293B)),
                    ),
                    const SizedBox(height: 24),
                    FilledButton.icon(
                      onPressed: () {
                        setState(() {
                          _dataFuture = _fetchData();
                        });
                      },
                      icon: const Icon(Icons.refresh),
                      label: const Text('Reîncearcă'),
                    ),
                  ],
                ),
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
            padding: const EdgeInsets.all(24),
            children: [
              if (activeSub != null) ...[
                const Text(
                  'Abonamentul tău',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                ),
                const SizedBox(height: 16),
                Container(
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF10B981), Color(0xFF059669)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF10B981).withOpacity(0.3),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.check_circle, color: Colors.white, size: 28),
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'Activ',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      Text(
                        activeSub.planNume,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Expiră la: ${_formatDate(activeSub.endDate)}',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                const Text(
                  'Planuri disponibile',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Nu poți achiziționa un alt abonament cât timp ai unul activ.',
                  style: TextStyle(color: Color(0xFF64748B), fontStyle: FontStyle.italic),
                ),
                const SizedBox(height: 16),
              ] else ...[
                const Text(
                  'Alege un plan',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Selectează abonamentul potrivit pentru tine.',
                  style: TextStyle(color: Color(0xFF64748B), fontSize: 16),
                ),
                const SizedBox(height: 24),
              ],
              if (plans.isEmpty)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Text('Nu există planuri de abonament disponibile.'),
                  ),
                )
              else
                ...plans.map((plan) => Card(
                      elevation: activeSub != null ? 0 : 2,
                      color: activeSub != null ? const Color(0xFFF1F5F9) : Colors.white,
                      margin: const EdgeInsets.only(bottom: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                        side: BorderSide(
                          color: activeSub != null ? Colors.transparent : const Color(0xFFE2E8F0),
                        ),
                      ),
                      child: InkWell(
                        borderRadius: BorderRadius.circular(16),
                        onTap: () => _selectPlan(plan, activeSub != null),
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: activeSub != null
                                      ? const Color(0xFFE2E8F0)
                                      : const Color(0xFFEFF6FF),
                                  shape: BoxShape.circle,
                                ),
                                child: Icon(
                                  Icons.star_rounded,
                                  color: activeSub != null ? const Color(0xFF94A3B8) : const Color(0xFF2563EB),
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      plan.nume,
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: activeSub != null ? const Color(0xFF94A3B8) : const Color(0xFF1E293B),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Valabilitate: ${plan.duration} zile',
                                      style: TextStyle(
                                        color: activeSub != null ? const Color(0xFF94A3B8) : const Color(0xFF64748B),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Text(
                                '${plan.price.toStringAsFixed(0)} RON',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: activeSub != null ? const Color(0xFF94A3B8) : const Color(0xFF10B981),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    )),
            ],
          );
        },
      ),
    );
  }
}
