import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:workforce_app/src/screens/shift_management_screen.dart';

void main() {
  group('ShiftManagementScreen Widget Tests', () {
    testWidgets('ShiftManagementScreen renders correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ShiftManagementScreen(),
          ),
        ),
      );

      // Verify the app bar title
      expect(find.text('Shift Management'), findsOneWidget);

      // Verify form fields are present
      expect(find.text('Shift Name'), findsOneWidget);
      expect(find.text('Shift Date'), findsOneWidget);
      expect(find.text('Shift Time'), findsOneWidget);

      // Verify submit button
      expect(find.text('Schedule Shift'), findsOneWidget);
    });

    testWidgets('Form validation works correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ShiftManagementScreen(),
          ),
        ),
      );

      // Try to submit empty form
      await tester.tap(find.text('Schedule Shift'));
      await tester.pump();

      // Verify validation errors appear
      expect(find.text('Please enter shift name'), findsOneWidget);
      expect(find.text('Please enter shift date'), findsOneWidget);
      expect(find.text('Please enter shift time'), findsOneWidget);
    });

    testWidgets('Can schedule shift with valid data', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ShiftManagementScreen(),
          ),
        ),
      );

      // Fill form fields
      await tester.enterText(find.byType(TextFormField).at(0), 'Morning Shift');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-01-15');
      await tester.enterText(find.byType(TextFormField).at(2), '09:00-17:00');

      // Submit form
      await tester.tap(find.text('Schedule Shift'));
      await tester.pump();

      // Verify shift appears in list
      expect(find.text('Morning Shift (2024-01-15 at 09:00-17:00)'), findsOneWidget);
      expect(find.text('Status: Scheduled'), findsOneWidget);
    });

    testWidgets('Can cancel scheduled shift', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ShiftManagementScreen(),
          ),
        ),
      );

      // Create a shift first
      await tester.enterText(find.byType(TextFormField).at(0), 'Evening Shift');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-02-01');
      await tester.enterText(find.byType(TextFormField).at(2), '17:00-01:00');
      await tester.tap(find.text('Schedule Shift'));
      await tester.pump();

      // Cancel the shift
      await tester.tap(find.byIcon(Icons.cancel));
      await tester.pump();

      // Verify status changed to Cancelled
      expect(find.text('Status: Cancelled'), findsOneWidget);
    });

    testWidgets('Multiple shifts are displayed correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ShiftManagementScreen(),
          ),
        ),
      );

      // Create first shift
      await tester.enterText(find.byType(TextFormField).at(0), 'Morning Shift');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-01-15');
      await tester.enterText(find.byType(TextFormField).at(2), '09:00-17:00');
      await tester.tap(find.text('Schedule Shift'));
      await tester.pump();

      // Create second shift
      await tester.enterText(find.byType(TextFormField).at(0), 'Night Shift');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-02-01');
      await tester.enterText(find.byType(TextFormField).at(2), '22:00-06:00');
      await tester.tap(find.text('Schedule Shift'));
      await tester.pump();

      // Verify both shifts are displayed
      expect(find.text('Morning Shift (2024-01-15 at 09:00-17:00)'), findsOneWidget);
      expect(find.text('Night Shift (2024-02-01 at 22:00-06:00)'), findsOneWidget);
    });

    testWidgets('Cancel button only appears for scheduled shifts', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ShiftManagementScreen(),
          ),
        ),
      );

      // Create a shift first
      await tester.enterText(find.byType(TextFormField).at(0), 'Test Shift');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-03-01');
      await tester.enterText(find.byType(TextFormField).at(2), '10:00-18:00');
      await tester.tap(find.text('Schedule Shift'));
      await tester.pump();

      // Verify cancel button is present for scheduled shift
      expect(find.byIcon(Icons.cancel), findsOneWidget);

      // Cancel the shift
      await tester.tap(find.byIcon(Icons.cancel));
      await tester.pump();

      // Verify cancel button is no longer present for cancelled shift
      expect(find.byIcon(Icons.cancel), findsNothing);
    });

    testWidgets('Form clears after successful submission', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: ShiftManagementScreen(),
          ),
        ),
      );

      // Fill form fields
      await tester.enterText(find.byType(TextFormField).at(0), 'Test Shift');
      await tester.enterText(find.byType(TextFormField).at(1), '2024-03-01');
      await tester.enterText(find.byType(TextFormField).at(2), '10:00-18:00');

      // Submit form
      await tester.tap(find.text('Schedule Shift'));
      await tester.pump();

      // Verify form fields are cleared
      expect(find.text('Test Shift'), findsOneWidget); // In the list
      expect(find.text('2024-03-01'), findsOneWidget); // In the list
      expect(find.text('10:00-18:00'), findsOneWidget); // In the list

      // But not in the form fields (they should be empty)
      final textFields = find.byType(TextFormField);
      expect((tester.widget(textFields.at(0)) as TextFormField).controller?.text, '');
      expect((tester.widget(textFields.at(1)) as TextFormField).controller?.text, '');
      expect((tester.widget(textFields.at(2)) as TextFormField).controller?.text, '');
    });
  });
}
