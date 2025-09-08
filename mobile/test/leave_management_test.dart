import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/screens/leave_management_screen.dart';

void main() {
  group('LeaveManagementScreen Widget Tests', () {
    testWidgets('LeaveManagementScreen renders correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: LeaveManagementScreen(),
          ),
        ),
      );

      // Verify the app bar title
      expect(find.text('Leave Management'), findsOneWidget);

      // Verify form fields are present
      expect(find.text('Leave Type'), findsOneWidget);
      expect(find.text('Start Date'), findsOneWidget);
      expect(find.text('End Date'), findsOneWidget);

      // Verify submit button
      expect(find.text('Submit Leave Request'), findsOneWidget);
    });

    testWidgets('Form validation works correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: LeaveManagementScreen(),
          ),
        ),
      );

      // Try to submit empty form
      await tester.tap(find.text('Submit Leave Request'));
      await tester.pump();

      // Verify validation errors appear
      expect(find.text('Please enter leave type'), findsOneWidget);
      expect(find.text('Please enter start date'), findsOneWidget);
      expect(find.text('Please enter end date'), findsOneWidget);
    });

    testWidgets('Can submit leave request with valid data', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: LeaveManagementScreen(),
          ),
        ),
      );

      // Fill form fields
      await tester.enterText(find.byType(TextFormField).at(0), 'Vacation');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-01-15');
      await tester.enterText(find.byType(TextFormField).at(2), '2024-01-20');

      // Submit form
      await tester.tap(find.text('Submit Leave Request'));
      await tester.pump();

      // Verify leave request appears in list
      expect(find.text('Vacation (2024-01-15 - 2024-01-20)'), findsOneWidget);
      expect(find.text('Status: Pending'), findsOneWidget);
    });

    testWidgets('Can approve leave request', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: LeaveManagementScreen(),
          ),
        ),
      );

      // Create a leave request first
      await tester.enterText(find.byType(TextFormField).at(0), 'Sick Leave');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-02-01');
      await tester.enterText(find.byType(TextFormField).at(2), '2024-02-02');
      await tester.tap(find.text('Submit Leave Request'));
      await tester.pump();

      // Approve the request
      await tester.tap(find.byIcon(Icons.check));
      await tester.pump();

      // Verify status changed to Approved
      expect(find.text('Status: Approved'), findsOneWidget);
    });

    testWidgets('Can reject leave request', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: LeaveManagementScreen(),
          ),
        ),
      );

      // Create a leave request first
      await tester.enterText(find.byType(TextFormField).at(0), 'Personal Leave');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-03-01');
      await tester.enterText(find.byType(TextFormField).at(2), '2024-03-05');
      await tester.tap(find.text('Submit Leave Request'));
      await tester.pump();

      // Reject the request
      await tester.tap(find.byIcon(Icons.close));
      await tester.pump();

      // Verify status changed to Rejected
      expect(find.text('Status: Rejected'), findsOneWidget);
    });

    testWidgets('Multiple leave requests are displayed correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: LeaveManagementScreen(),
          ),
        ),
      );

      // Create first leave request
      await tester.enterText(find.byType(TextFormField).at(0), 'Vacation');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-01-15');
      await tester.enterText(find.byType(TextFormField).at(2), '2024-01-20');
      await tester.tap(find.text('Submit Leave Request'));
      await tester.pump();

      // Create second leave request
      await tester.enterText(find.byType(TextFormField).at(0), 'Sick Leave');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-02-01');
      await tester.enterText(find.byType(TextFormField).at(2), '2024-02-02');
      await tester.tap(find.text('Submit Leave Request'));
      await tester.pump();

      // Verify both requests are displayed
      expect(find.text('Vacation (2024-01-15 - 2024-01-20)'), findsOneWidget);
      expect(find.text('Sick Leave (2024-02-01 - 2024-02-02)'), findsOneWidget);
    });
  });
}
