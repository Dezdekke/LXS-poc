import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class StockPage extends StatefulWidget {
  const StockPage({super.key});

  @override
  State<StockPage> createState() => _StockPageState();
}

class _StockPageState extends State<StockPage> {
  List<dynamic> _content = [];
  int _currentIndex = 0;
  final countLabel = 'Telling';
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;
  String? _id;

  Future<void> _fetchStock() async {
    setState(() => _isLoading = true);
    final response =
        await http.get(Uri.parse('http://192.168.1.21:8000/stock-json'));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        _id = data['id'];
        _content = data['content'];
        _controller.text = '';
        _isLoading = false;
      });
    } else {
      setState(() => _isLoading = false);
    }
  }

  void _nextItem() {
    if (_controller.text.isNotEmpty) {
      _content[_currentIndex][countLabel] = int.tryParse(_controller.text) ?? 0;
      if (_currentIndex < _content.length - 1) {
        setState(() {
          _currentIndex++;
          _controller.text = '';
        });
      } else {
        _submitStock();
      }
    }
  }

  Future<void> _submitStock() async {
    final updatedData = {'id': _id, 'content': _content};
    await http.post(
      Uri.parse('http://192.168.1.21:8000/stock-excel-results'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(updatedData),
    );
    Navigator.pop(context);
  }

  @override
  void initState() {
    super.initState();
    _fetchStock();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Stock Entry')),
      body: Center(
        child: _isLoading
            ? const CircularProgressIndicator()
            : _content.isEmpty
                ? const Text('No data available')
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Artnr: ${_content[_currentIndex]['Artnr.']}'),
                      Text('Product: ${_content[_currentIndex]['Art. naam']}'),
                      TextField(
                        controller: _controller,
                        keyboardType: TextInputType.number,
                        decoration:
                            const InputDecoration(labelText: 'Enter count'),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: _nextItem,
                        child: Text(_currentIndex < _content.length - 1
                            ? 'Next'
                            : 'Submit'),
                      ),
                    ],
                  ),
      ),
    );
  }
}
