import 'package:flutter/material.dart';

class LeaveManagementScreen extends StatefulWidget {
  @override
  _LeaveManagementScreenState createState() => _LeaveManagementScreenState();
}

class _LeaveManagementScreenState extends State<LeaveManagementScreen> {
  final _formKey = GlobalKey<FormState>();
  final List<Map<String, dynamic>> _leaveRequests = [];

  final TextEditingController _leaveTypeController = TextEditingController();
  final TextEditingController _startDateController = TextEditingController();
  final TextEditingController _endDateController = TextEditingController();

  void _submitLeaveRequest() {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _leaveRequests.add({
          'leaveType': _leaveTypeController.text,
          'startDate': _startDateController.text,
          'endDate': _endDateController.text,
          'status': 'Pending',
        });
        _leaveTypeController.clear();
        _startDateController.clear();
        _endDateController.clear();
      });
    }
  }

  void _approveRequest(int index) {
    setState(() {
      _leaveRequests[index]['status'] = 'Approved';
    });
  }

  void _rejectRequest(int index) {
    setState(() {
      _leaveRequests[index]['status'] = 'Rejected';
    });
  }

  @override
  void dispose() {
    _leaveTypeController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Leave Management'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    controller: _leaveTypeController,
                    decoration: InputDecoration(labelText: 'Leave Type'),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter leave type';
                      }
                      return null;
                    },
                  ),
                  TextFormField(
                    controller: _startDateController,
                    decoration: InputDecoration(labelText: 'Start Date'),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter start date';
                      }
                      return null;
                    },
                  ),
                  TextFormField(
                    controller: _endDateController,
                    decoration: InputDecoration(labelText: 'End Date'),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter end date';
                      }
                      return null;
                    },
                  ),
                  SizedBox(height: 10),
                  ElevatedButton(
                    onPressed: _submitLeaveRequest,
                    child: Text('Submit Leave Request'),
                  ),
                ],
              ),
            ),
            SizedBox(height: 20),
            Expanded(
              child: ListView.builder(
                itemCount: _leaveRequests.length,
                itemBuilder: (context, index) {
                  final request = _leaveRequests[index];
                  return Card(
                    child: ListTile(
                      title: Text('${request['leaveType']} (${request['startDate']} - ${request['endDate']})'),
                      subtitle: Text('Status: ${request['status']}'),
                      trailing: request['status'] == 'Pending'
                          ? Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: Icon(Icons.check, color: Colors.green),
                                  onPressed: () => _approveRequest(index),
                                ),
                                IconButton(
                                  icon: Icon(Icons.close, color: Colors.red),
                                  onPressed: () => _rejectRequest(index),
                                ),
                              ],
                            )
                          : null,
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
