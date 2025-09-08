import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/services/api_service.dart';
import 'package:flutter/material.dart'; // Import for SnackBar

class Company {
  final int id;
  final String name;
  final String? domain;
  final String? contactEmail;
  final String? contactPhone;
  final String? address;
  final String? city;
  final String? state;
  final String? country;
  final String? postalCode;
  final DateTime createdAt;
  final DateTime updatedAt;

  Company({
    required this.id,
    required this.name,
    this.domain,
    this.contactEmail,
    this.contactPhone,
    this.address,
    this.city,
    this.state,
    this.country,
    this.postalCode,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Company.fromJson(Map<String, dynamic> json) {
    return Company(
      id: json['id'],
      name: json['name'],
      domain: json['domain'],
      contactEmail: json['contact_email'],
      contactPhone: json['contact_phone'],
      address: json['address'],
      city: json['city'],
      state: json['state'],
      country: json['country'],
      postalCode: json['postal_code'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}

class CompaniesState {
  final List<Company> companies;
  final bool isLoading;
  final String? error;

  CompaniesState({
    this.companies = const [],
    this.isLoading = false,
    this.error,
  });

  CompaniesState copyWith({
    List<Company>? companies,
    bool? isLoading,
    String? error,
  }) {
    return CompaniesState(
      companies: companies ?? this.companies,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class CompaniesNotifier extends StateNotifier<CompaniesState> {
  final ApiService _apiService;

  CompaniesNotifier(this._apiService) : super(CompaniesState());

  Future<void> fetchCompanies() async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _apiService.getCompanies();
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        final companies = data.map((companyJson) => Company.fromJson(companyJson)).toList();
        
        state = state.copyWith(
          companies: companies,
          isLoading: false,
          error: null,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Failed to fetch companies: ${response.statusCode}',
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Network error: ${e.toString()}',
      );
    }
  }

  Future<void> createCompany(BuildContext context, String name) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _apiService.post('/companies/', {
        'name': name,
      });
      
      if (response.statusCode == 201) {
        // Refresh the companies list after successful creation
        await fetchCompanies();
        // Show success notification
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Company created successfully!')),
          );
        }
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Failed to create company: ${response.statusCode}',
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Network error: ${e.toString()}',
      );
    }
  }

  Future<void> deleteCompany(BuildContext context, int companyId) async {
    state = state.copyWith(isLoading: true, error: null);
    
    // Show confirmation dialog
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Confirm Deletion'),
        content: Text('Are you sure you want to delete this company?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        final response = await _apiService.delete('/companies/$companyId');
        
        if (response.statusCode == 200) {
          // Refresh the companies list after successful deletion
          await fetchCompanies();
          // Show success notification
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Company deleted successfully!')),
            );
          }
        } else {
          state = state.copyWith(
            isLoading: false,
            error: 'Failed to delete company: ${response.statusCode}',
          );
        }
      } catch (e) {
        state = state.copyWith(
          isLoading: false,
          error: 'Network error: ${e.toString()}',
        );
      }
    } else {
      state = state.copyWith(isLoading: false); // Reset loading state if canceled
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

final companiesProvider = StateNotifierProvider<CompaniesNotifier, CompaniesState>((ref) {
  final apiService = ApiService();
  return CompaniesNotifier(apiService);
});
