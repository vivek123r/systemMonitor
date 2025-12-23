import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'auth_service.dart';
import 'login_page.dart';

class RemoteControlPage extends StatefulWidget {
  const RemoteControlPage({super.key});

  @override
  State<RemoteControlPage> createState() => _RemoteControlPageState();
}

class _RemoteControlPageState extends State<RemoteControlPage> {
  static const String baseUrl = 'https://system-monitor-silk.vercel.app/api';

  final AuthService _authService = AuthService();
  String? _selectedDeviceId;
  List<Map<String, dynamic>> _devices = [];
  bool _isLoadingDevices = true;

  double _brightnessValue = 50.0;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadDevices();
  }

  Future<Map<String, String>> _getAuthHeaders() async {
    final token = await _authService.getIdToken();
    final userId = _authService.userId;
    final deviceId = _selectedDeviceId ?? 'unknown';

    return {
      'Content-Type': 'application/json',
      'X-User-ID': userId ?? '',
      'X-Device-ID': deviceId,
      'Authorization': 'Bearer ${token ?? ''}',
    };
  }

  Future<void> _loadDevices() async {
    setState(() => _isLoadingDevices = true);

    try {
      final headers = await _getAuthHeaders();
      final response = await http.get(
        Uri.parse('$baseUrl/devices'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _devices = List<Map<String, dynamic>>.from(data['devices'] ?? []);
          if (_devices.isNotEmpty && _selectedDeviceId == null) {
            _selectedDeviceId = _devices[0]['device_id'];
          }
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error loading devices: $e')));
      }
    } finally {
      setState(() => _isLoadingDevices = false);
    }
  }

  Future<void> sendCommand(
    String command, {
    Map<String, dynamic>? params,
  }) async {
    if (_selectedDeviceId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a device first')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final headers = await _getAuthHeaders();
      final response = await http.post(
        Uri.parse('$baseUrl/command?target_device_id=$_selectedDeviceId'),
        headers: headers,
        body: json.encode({'command': command, 'params': params ?? {}}),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Command "$command" sent successfully!'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 2),
            ),
          );
        }
      } else {
        throw Exception('Failed to send command: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<bool> confirmAction(String title, String message) async {
    return await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: Text(title),
            content: Text(message),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                child: const Text('Confirm'),
              ),
            ],
          ),
        ) ??
        false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Remote Control'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          // Sign out button
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await _authService.signOut();
              if (mounted) {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const LoginPage()),
                );
              }
            },
          ),
        ],
      ),
      body: _isLoadingDevices
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Device Selector
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Select Device',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 12),
                          if (_devices.isEmpty)
                            const Text('No devices connected')
                          else
                            DropdownButtonFormField<String>(
                              value: _selectedDeviceId,
                              decoration: const InputDecoration(
                                border: OutlineInputBorder(),
                                labelText: 'Device',
                              ),
                              items: _devices.map((device) {
                                final deviceId = device['device_id'] as String;
                                final stats = device['stats'];
                                final osName =
                                    stats?['system']?['os_name'] ?? 'Unknown';
                                return DropdownMenuItem<String>(
                                  value: deviceId,
                                  child: Text('$deviceId ($osName)'),
                                );
                              }).toList(),
                              onChanged: (value) {
                                setState(() {
                                  _selectedDeviceId = value;
                                });
                              },
                            ),
                          const SizedBox(height: 8),
                          ElevatedButton.icon(
                            onPressed: _loadDevices,
                            icon: const Icon(Icons.refresh),
                            label: const Text('Refresh Devices'),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Warning Card
                  Card(
                    color: Colors.orange[100],
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Icon(
                            Icons.warning_amber,
                            color: Colors.orange[800],
                            size: 32,
                          ),
                          const SizedBox(width: 12),
                          const Expanded(
                            child: Text(
                              'Use remote commands carefully! Some actions will affect your PC immediately.',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Power Commands
                  _buildSectionTitle(
                    'Power Management',
                    Icons.power_settings_new,
                  ),
                  _buildControlCard(
                    icon: Icons.power_settings_new,
                    title: 'Shutdown',
                    subtitle: 'Turn off the PC',
                    color: Colors.red,
                    onTap: () async {
                      if (await confirmAction(
                        'Shutdown PC',
                        'Are you sure you want to shutdown the PC?',
                      )) {
                        sendCommand('shutdown');
                      }
                    },
                  ),
                  _buildControlCard(
                    icon: Icons.restart_alt,
                    title: 'Restart',
                    subtitle: 'Restart the PC',
                    color: Colors.orange,
                    onTap: () async {
                      if (await confirmAction(
                        'Restart PC',
                        'Are you sure you want to restart the PC?',
                      )) {
                        sendCommand('restart');
                      }
                    },
                  ),
                  _buildControlCard(
                    icon: Icons.bedtime,
                    title: 'Sleep',
                    subtitle: 'Put PC to sleep',
                    color: Colors.blue,
                    onTap: () => sendCommand('sleep'),
                  ),
                  _buildControlCard(
                    icon: Icons.exit_to_app,
                    title: 'Logoff',
                    subtitle: 'Log out current user',
                    color: Colors.purple,
                    onTap: () async {
                      if (await confirmAction(
                        'Logoff',
                        'Are you sure you want to log off?',
                      )) {
                        sendCommand('logoff');
                      }
                    },
                  ),

                  const SizedBox(height: 24),

                  // Power Profiles
                  _buildSectionTitle('Power Profiles', Icons.speed),
                  _buildControlCard(
                    icon: Icons.flash_on,
                    title: 'High Performance',
                    subtitle: 'Maximum performance',
                    color: Colors.red,
                    onTap: () => sendCommand('power_high'),
                  ),
                  _buildControlCard(
                    icon: Icons.balance,
                    title: 'Balanced',
                    subtitle: 'Balance performance and energy',
                    color: Colors.green,
                    onTap: () => sendCommand('power_balanced'),
                  ),
                  _buildControlCard(
                    icon: Icons.battery_saver,
                    title: 'Power Saver',
                    subtitle: 'Maximize battery life',
                    color: Colors.blue,
                    onTap: () => sendCommand('power_saver'),
                  ),

                  const SizedBox(height: 24),

                  // Brightness Control
                  _buildSectionTitle('Screen Brightness', Icons.brightness_6),
                  Card(
                    elevation: 4,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(
                                Icons.brightness_6,
                                color: Colors.amber,
                              ),
                              const SizedBox(width: 12),
                              Text(
                                'Brightness: ${_brightnessValue.round()}%',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          Slider(
                            value: _brightnessValue,
                            min: 0,
                            max: 100,
                            divisions: 20,
                            label: '${_brightnessValue.round()}%',
                            onChanged: (value) {
                              setState(() => _brightnessValue = value);
                            },
                          ),
                          ElevatedButton.icon(
                            onPressed: () => sendCommand(
                              'brightness',
                              params: {'value': _brightnessValue.round()},
                            ),
                            icon: const Icon(Icons.check),
                            label: const Text('Apply Brightness'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.amber,
                              minimumSize: const Size.fromHeight(45),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Quick Actions
                  _buildSectionTitle('Quick Actions', Icons.bolt),
                  _buildControlCard(
                    icon: Icons.camera_alt,
                    title: 'Take Screenshot',
                    subtitle: 'Capture the screen',
                    color: Colors.teal,
                    onTap: () => sendCommand('screenshot'),
                  ),
                  _buildControlCard(
                    icon: Icons.open_in_new,
                    title: 'Open Notepad',
                    subtitle: 'Launch notepad.exe',
                    color: Colors.indigo,
                    onTap: () =>
                        sendCommand('open_app', params: {'app': 'notepad.exe'}),
                  ),
                  _buildControlCard(
                    icon: Icons.web,
                    title: 'Open Chrome',
                    subtitle: 'Launch Google Chrome',
                    color: Colors.green,
                    onTap: () =>
                        sendCommand('open_app', params: {'app': 'chrome.exe'}),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildSectionTitle(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Icon(icon, color: Colors.indigo[700]),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.indigo[700],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControlCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 3,
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.2),
          child: Icon(icon, color: color),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }
}
