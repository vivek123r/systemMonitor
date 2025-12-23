import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'login_page.dart';
import 'remote_control_page.dart';

// TODO: Replace with your Firebase configuration
// Get this from Firebase Console > Project Settings > Your apps > Web app
const firebaseConfig = {
  'apiKey': 'AIzaSyCfcUxvGb4q9AQRiSLIHAdAH4Kt8zaTUpc',
  'appId': '1:280248422582:web:5c7f17f949f8990e5a5617',
  'messagingSenderId': '280248422582',
  'projectId': 'system-monitor-4dd1f',
  'authDomain': 'system-monitor-4dd1f.firebaseapp.com',
  'storageBucket': 'system-monitor-4dd1f.firebasestorage.app',
};

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase
  try {
    await Firebase.initializeApp(
      options: FirebaseOptions(
        apiKey: firebaseConfig['apiKey']!,
        appId: firebaseConfig['appId']!,
        messagingSenderId: firebaseConfig['messagingSenderId']!,
        projectId: firebaseConfig['projectId']!,
      ),
    );
  } catch (e) {
    print('Firebase initialization error: $e');
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'System Monitor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      // Check authentication state
      home: StreamBuilder<User?>(
        stream: FirebaseAuth.instance.authStateChanges(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }

          if (snapshot.hasData) {
            return const RemoteControlPage();
          }

          return const LoginPage();
        },
      ),
    );
  }
}

class SystemMonitorPage extends StatefulWidget {
  const SystemMonitorPage({super.key});

  @override
  State<SystemMonitorPage> createState() => _SystemMonitorPageState();
}

class _SystemMonitorPageState extends State<SystemMonitorPage> {
  static const String apiUrl =
      'https://system-monitor-silk.vercel.app/api/status';

  Map<String, dynamic> stats = {
    'cpu': 0.0,
    'ram': 0.0,
    'gpu': 0.0,
    'disk': {},
    'status': 'Loading...',
  };

  Timer? _timer;
  bool _isLoading = true;
  String? _error;
  DateTime? _lastUpdate;

  // Expansion states for collapsible sections
  bool _cpuDetailsExpanded = false;
  bool _ramDetailsExpanded = false;
  bool _gpuDetailsExpanded = false;
  bool _diskDetailsExpanded = false;
  bool _networkDetailsExpanded = false;
  bool _processesExpanded = false;

  @override
  void initState() {
    super.initState();
    fetchStats();
    _timer = Timer.periodic(const Duration(seconds: 2), (timer) {
      fetchStats();
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> fetchStats() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        setState(() {
          stats = json.decode(response.body);
          _isLoading = false;
          _error = null;
          _lastUpdate = DateTime.now();
        });
      } else {
        setState(() {
          _error = 'Server error: ${response.statusCode}';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Connection error: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('System Monitor'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_remote),
            tooltip: 'Remote Control',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const RemoteControlPage(),
                ),
              );
            },
          ),
          if (_lastUpdate != null)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Center(
                child: Text(
                  'Updated: ${_lastUpdate!.hour}:${_lastUpdate!.minute.toString().padLeft(2, '0')}:${_lastUpdate!.second.toString().padLeft(2, '0')}',
                  style: const TextStyle(fontSize: 12),
                ),
              ),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, color: Colors.red, size: 64),
                  const SizedBox(height: 16),
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: fetchStats,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: fetchStats,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildSystemInfoCard(),
                  const SizedBox(height: 16),
                  if (stats['battery'] != null) ...[
                    _buildBatteryCard(),
                    const SizedBox(height: 16),
                  ],
                  _buildStatusCard(),
                  const SizedBox(height: 16),
                  _buildStatCard(
                    'CPU Usage',
                    stats['cpu'],
                    Icons.memory,
                    Colors.blue,
                    onTap: stats['cpu_details'] != null
                        ? () => setState(
                            () => _cpuDetailsExpanded = !_cpuDetailsExpanded,
                          )
                        : null,
                    isExpanded: _cpuDetailsExpanded,
                  ),
                  if (stats['cpu_details'] != null && _cpuDetailsExpanded)
                    _buildCPUDetails(),
                  const SizedBox(height: 16),
                  _buildStatCard(
                    'RAM Usage',
                    stats['ram'],
                    Icons.storage,
                    Colors.green,
                    onTap: stats['ram_details'] != null
                        ? () => setState(
                            () => _ramDetailsExpanded = !_ramDetailsExpanded,
                          )
                        : null,
                    isExpanded: _ramDetailsExpanded,
                  ),
                  if (stats['ram_details'] != null && _ramDetailsExpanded)
                    _buildRAMDetails(),
                  const SizedBox(height: 16),
                  _buildStatCard(
                    'GPU Usage',
                    stats['gpu'],
                    Icons.videocam,
                    Colors.orange,
                    onTap: stats['gpu_details'] != null
                        ? () => setState(
                            () => _gpuDetailsExpanded = !_gpuDetailsExpanded,
                          )
                        : null,
                    isExpanded: _gpuDetailsExpanded,
                  ),
                  if (stats['gpu_details'] != null && _gpuDetailsExpanded)
                    _buildGPUDetails(),
                  const SizedBox(height: 16),
                  _buildDiskCards(),
                  if (stats['network'] != null) ...[
                    const SizedBox(height: 16),
                    _buildNetworkCard(),
                  ],
                  if (stats['processes'] != null) ...[
                    const SizedBox(height: 16),
                    _buildProcessesCard(),
                  ],
                ],
              ),
            ),
    );
  }

  // System Info Card (OS Name, Hostname, Uptime)
  Widget _buildSystemInfoCard() {
    final system = stats['system'] as Map<String, dynamic>?;
    if (system == null) return const SizedBox.shrink();

    return Card(
      elevation: 4,
      color: Colors.indigo[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.computer, color: Colors.indigo[700], size: 32),
                const SizedBox(width: 12),
                Text(
                  'System Information',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.indigo[700],
                  ),
                ),
              ],
            ),
            const Divider(height: 24),

            // Highlight CPU Model
            if (system['cpu_model'] != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.blue[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.memory, color: Colors.blue, size: 24),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'CPU',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            system['cpu_model'],
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // Highlight GPU Model
            if (system['gpu_model'] != null &&
                system['gpu_model'] != 'No GPU detected') ...[
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.orange[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.videocam, color: Colors.orange, size: 24),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'GPU',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            system['gpu_model'],
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const Divider(height: 12),
            _buildInfoRow('Operating System', system['os_name'] ?? 'Unknown'),
            _buildInfoRow('Version', system['os_version'] ?? 'Unknown'),
            _buildInfoRow('Hostname', system['hostname'] ?? 'Unknown'),
            _buildInfoRow('Architecture', system['architecture'] ?? 'Unknown'),
            _buildInfoRow('Uptime', '${system['uptime_hours']} hours'),
            _buildInfoRow('Boot Time', system['boot_time'] ?? 'Unknown'),
          ],
        ),
      ),
    );
  }

  // Battery Card
  Widget _buildBatteryCard() {
    final battery = stats['battery'] as Map<String, dynamic>?;
    if (battery == null) return const SizedBox.shrink();

    final percent = battery['percent'] ?? 0.0;
    final plugged = battery['plugged'] ?? false;
    final timeLeft = battery['time_left_str'] ?? 'Unknown';

    Color batteryColor;
    IconData batteryIcon;

    if (plugged) {
      batteryColor = Colors.green;
      batteryIcon = Icons.battery_charging_full;
    } else if (percent > 50) {
      batteryColor = Colors.green;
      batteryIcon = Icons.battery_full;
    } else if (percent > 20) {
      batteryColor = Colors.orange;
      batteryIcon = Icons.battery_3_bar;
    } else {
      batteryColor = Colors.red;
      batteryIcon = Icons.battery_alert;
    }

    return Card(
      elevation: 4,
      color: batteryColor.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(batteryIcon, color: batteryColor, size: 32),
                const SizedBox(width: 12),
                Text(
                  'Battery Status',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: batteryColor,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: percent / 100,
              backgroundColor: Colors.grey[300],
              color: batteryColor,
              minHeight: 24,
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${percent.toStringAsFixed(1)}%',
                  style: const TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      plugged ? 'Charging' : 'On Battery',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: batteryColor,
                      ),
                    ),
                    Text(
                      'Time: $timeLeft',
                      style: const TextStyle(fontSize: 14, color: Colors.grey),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard() {
    final isOnline = stats['status'] == 'Online';
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              isOnline ? Icons.check_circle : Icons.error,
              color: isOnline ? Colors.green : Colors.red,
              size: 32,
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Status: ${stats['status']}',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (isOnline)
                  const Text(
                    'Agent is sending data',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(
    String title,
    dynamic value,
    IconData icon,
    Color color, {
    VoidCallback? onTap,
    bool isExpanded = false,
  }) {
    final percentage = value is num ? value.toDouble() : 0.0;

    return Card(
      elevation: 4,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, color: color, size: 28),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (onTap != null)
                    Icon(
                      isExpanded ? Icons.expand_less : Icons.expand_more,
                      color: Colors.grey,
                    ),
                ],
              ),
              const SizedBox(height: 16),
              LinearProgressIndicator(
                value: percentage / 100,
                backgroundColor: Colors.grey[300],
                color: color,
                minHeight: 24,
              ),
              const SizedBox(height: 8),
              Text(
                '${percentage.toStringAsFixed(1)}%',
                style: const TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // CPU Details
  Widget _buildCPUDetails() {
    final details = stats['cpu_details'] as Map<String, dynamic>?;
    if (details == null) return const SizedBox.shrink();

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(top: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'CPU Details',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const Divider(),
            _buildInfoRow(
              'Physical Cores',
              '${details['core_count_physical']}',
            ),
            _buildInfoRow('Logical Cores', '${details['core_count_logical']}'),
            _buildInfoRow(
              'Current Frequency',
              '${details['frequency_current']} MHz',
            ),
            _buildInfoRow('Min Frequency', '${details['frequency_min']} MHz'),
            _buildInfoRow('Max Frequency', '${details['frequency_max']} MHz'),
            const SizedBox(height: 8),
            const Text(
              'Per-Core Usage:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: (details['per_core'] as List<dynamic>)
                  .asMap()
                  .entries
                  .map((entry) {
                    return Chip(
                      label: Text(
                        'Core ${entry.key}: ${entry.value.toStringAsFixed(1)}%',
                      ),
                      backgroundColor: Colors.blue[100],
                    );
                  })
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }

  // RAM Details
  Widget _buildRAMDetails() {
    final details = stats['ram_details'] as Map<String, dynamic>?;
    final swapDetails = stats['swap_details'] as Map<String, dynamic>?;
    if (details == null) return const SizedBox.shrink();

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(top: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'RAM Details',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const Divider(),
            _buildInfoRow('Total', '${details['total_gb']} GB'),
            _buildInfoRow('Used', '${details['used_gb']} GB'),
            _buildInfoRow('Available', '${details['available_gb']} GB'),
            _buildInfoRow('Free', '${details['free_gb']} GB'),
            if (swapDetails != null) ...[
              const SizedBox(height: 8),
              const Text(
                'Swap Memory:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const Divider(),
              _buildInfoRow('Total', '${swapDetails['total_gb']} GB'),
              _buildInfoRow('Used', '${swapDetails['used_gb']} GB'),
              _buildInfoRow('Free', '${swapDetails['free_gb']} GB'),
              _buildInfoRow('Usage', '${swapDetails['percent']}%'),
            ],
          ],
        ),
      ),
    );
  }

  // GPU Details
  Widget _buildGPUDetails() {
    final details = stats['gpu_details'] as List<dynamic>?;
    if (details == null || details.isEmpty) return const SizedBox.shrink();

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(top: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'GPU Details',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const Divider(),
            ...details.map((gpu) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildInfoRow('Name', gpu['name']),
                  _buildInfoRow('Load', '${gpu['load_percent']}%'),
                  _buildInfoRow('Memory Used', '${gpu['memory_used_mb']} MB'),
                  _buildInfoRow('Memory Total', '${gpu['memory_total_mb']} MB'),
                  _buildInfoRow('Memory Usage', '${gpu['memory_percent']}%'),
                  _buildInfoRow('Temperature', '${gpu['temperature_c']}°C'),
                  if (details.indexOf(gpu) < details.length - 1)
                    const Divider(),
                ],
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildDiskCards() {
    final diskDetails = stats['disk_details'] as Map<String, dynamic>?;
    if (diskDetails == null || diskDetails.isEmpty) {
      return const Card(
        elevation: 4,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No disk data available'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.only(bottom: 8),
          child: Text(
            'Disk Usage',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
        ),
        ...diskDetails.entries.map((entry) {
          final details = entry.value as Map<String, dynamic>;
          final diskIndex = diskDetails.keys.toList().indexOf(entry.key);
          final isExpanded = _diskDetailsExpanded;

          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Card(
              elevation: 4,
              child: InkWell(
                onTap: () => setState(
                  () => _diskDetailsExpanded = !_diskDetailsExpanded,
                ),
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(
                            Icons.sd_storage,
                            color: Colors.purple,
                            size: 28,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Drive ${entry.key}:',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          Icon(
                            isExpanded ? Icons.expand_less : Icons.expand_more,
                            color: Colors.grey,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      LinearProgressIndicator(
                        value: details['usage_percent'] / 100,
                        backgroundColor: Colors.grey[300],
                        color: Colors.purple,
                        minHeight: 24,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${details['usage_percent']}%',
                        style: const TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (isExpanded) ...[
                        const Divider(height: 24),
                        _buildInfoRow('Total', '${details['total_gb']} GB'),
                        _buildInfoRow('Used', '${details['used_gb']} GB'),
                        _buildInfoRow('Free', '${details['free_gb']} GB'),
                        _buildInfoRow('Filesystem', details['filesystem']),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          );
        }).toList(),
        if (stats['disk_io'] != null && _diskDetailsExpanded)
          _buildDiskIOCard(),
      ],
    );
  }

  Widget _buildDiskIOCard() {
    final diskIO = stats['disk_io'] as Map<String, dynamic>?;
    if (diskIO == null) return const SizedBox.shrink();

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(top: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Disk I/O Statistics',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const Divider(),
            _buildInfoRow(
              'Read',
              '${diskIO['read_mb']} MB (${diskIO['read_count']} ops)',
            ),
            _buildInfoRow(
              'Write',
              '${diskIO['write_mb']} MB (${diskIO['write_count']} ops)',
            ),
            _buildInfoRow('Read Time', '${diskIO['read_time_ms']} ms'),
            _buildInfoRow('Write Time', '${diskIO['write_time_ms']} ms'),
          ],
        ),
      ),
    );
  }

  Widget _buildNetworkCard() {
    final network = stats['network'] as Map<String, dynamic>?;
    if (network == null) return const SizedBox.shrink();

    return Card(
      elevation: 4,
      child: InkWell(
        onTap: () =>
            setState(() => _networkDetailsExpanded = !_networkDetailsExpanded),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.network_check, color: Colors.teal, size: 28),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Text(
                      'Network Statistics',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Icon(
                    _networkDetailsExpanded
                        ? Icons.expand_less
                        : Icons.expand_more,
                    color: Colors.grey,
                  ),
                ],
              ),
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      const Icon(
                        Icons.arrow_downward,
                        color: Colors.green,
                        size: 32,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${network['bytes_recv_mb']} MB',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${network['packets_recv']} packets',
                        style: const TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                  Column(
                    children: [
                      const Icon(
                        Icons.arrow_upward,
                        color: Colors.orange,
                        size: 32,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${network['bytes_sent_mb']} MB',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${network['packets_sent']} packets',
                        style: const TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                ],
              ),
              if (_networkDetailsExpanded) ...[
                const Divider(height: 24),
                _buildInfoRow('Errors In', '${network['errors_in']}'),
                _buildInfoRow('Errors Out', '${network['errors_out']}'),
                _buildInfoRow('Dropped In', '${network['drop_in']}'),
                _buildInfoRow('Dropped Out', '${network['drop_out']}'),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProcessesCard() {
    final processes = stats['processes'] as Map<String, dynamic>?;
    if (processes == null) return const SizedBox.shrink();

    final topCPU = processes['top_cpu'] as List<dynamic>?;
    final topMemory = processes['top_memory'] as List<dynamic>?;

    return Card(
      elevation: 4,
      child: InkWell(
        onTap: () => setState(() => _processesExpanded = !_processesExpanded),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.apps, color: Colors.deepOrange, size: 28),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Top Processes (${processes['total_processes']} total)',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Icon(
                    _processesExpanded ? Icons.expand_less : Icons.expand_more,
                    color: Colors.grey,
                  ),
                ],
              ),
              if (_processesExpanded) ...[
                const Divider(height: 24),
                if (topCPU != null) ...[
                  const Text(
                    'Top CPU Usage:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  ...topCPU.take(5).map((proc) {
                    return ListTile(
                      dense: true,
                      leading: const Icon(Icons.memory, size: 20),
                      title: Text(proc['name'] ?? 'Unknown'),
                      trailing: Text(
                        '${proc['cpu_percent']?.toStringAsFixed(1)}%',
                      ),
                    );
                  }).toList(),
                ],
                const Divider(height: 24),
                if (topMemory != null) ...[
                  const Text(
                    'Top Memory Usage:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  ...topMemory.take(5).map((proc) {
                    return ListTile(
                      dense: true,
                      leading: const Icon(Icons.storage, size: 20),
                      title: Text(proc['name'] ?? 'Unknown'),
                      trailing: Text(
                        '${proc['memory_percent']?.toStringAsFixed(1)}%',
                      ),
                    );
                  }).toList(),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
