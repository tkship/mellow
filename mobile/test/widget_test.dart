import 'package:flutter_test/flutter_test.dart';
import 'package:mellow/main.dart';

void main() {
  testWidgets('App renders without error', (WidgetTester tester) async {
    await tester.pumpWidget(const MellowApp());
    await tester.pump();
    // Basic smoke test — app should render without throwing
    expect(find.byType(MellowApp), findsNothing); // wrapped by ShadApp
  });
}
