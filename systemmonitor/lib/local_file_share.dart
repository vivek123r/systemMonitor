import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:file_picker/file_picker.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

class LocalFileSharePage extends StatefulWidget {
  const LocalFileSharePage({Key? key}) : super(key: key);

  @override
  State<LocalFileSharePage> createState() => _LocalFileSharePageState();
}

class _LocalFileSharePageState extends State<LocalFileSharePage> {
  MobileScannerController? scannerController;

  String? serverIp;
  String? serverToken;
  bool isConnected = false;
  bool isScanning = false;

  List<FileItem> files = [];
  bool isLoading = false;
  double uploadProgress = 0.0;
  String uploadStatus = '';

  final Dio dio = Dio();

  @override
  void initState() {
    super.initState();
    _loadSavedConnection();
  }

  @override
  void dispose() {
    scannerController?.dispose();
    super.dispose();
  }

  Future<void> _loadSavedConnection() async {
    final prefs = await SharedPreferences.getInstance();
    final ip = prefs.getString('local_server_ip');
    final token = prefs.getString('local_server_token');

    if (ip != null && token != null) {
      setState(() {
        serverIp = ip;
        serverToken = token;
        isConnected = true;
      });
      _loadFiles();
    }
  }

  Future<void> _saveConnection(String ip, String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('local_server_ip', ip);
    await prefs.setString('local_server_token', token);
  }

  void _handleQRDetection(BarcodeCapture capture) {
    final List<Barcode> barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;

    final String? code = barcodes.first.rawValue;
    if (code == null) return;

    try {
      final data = json.decode(code);
      final ip = data['ip'];
      final token = data['token'];

      setState(() {
        serverIp = ip;
        serverToken = token;
        isConnected = true;
        isScanning = false;
      });

      _saveConnection(ip, token);
      scannerController?.stop();
      _loadFiles();

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Connected to PC successfully!')),
      );
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Invalid QR code: $e')));
    }
  }

  Future<void> _loadFiles() async {
    if (serverIp == null || serverToken == null) return;

    setState(() => isLoading = true);

    try {
      final response = await dio.get(
        'http://$serverIp/list',
        options: Options(headers: {'X-Local-Token': serverToken}),
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final fileList = (data['files'] as List)
            .map((f) => FileItem.fromJson(f))
            .toList();

        setState(() {
          files = fileList;
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() => isLoading = false);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Failed to load files: $e')));
    }
  }

  Future<void> _uploadFile() async {
    if (serverIp == null || serverToken == null) return;

    try {
      final result = await FilePicker.platform.pickFiles();

      if (result != null && result.files.single.path != null) {
        final file = File(result.files.single.path!);
        final fileName = result.files.single.name;

        setState(() {
          uploadStatus = 'Uploading $fileName...';
          uploadProgress = 0.0;
        });

        final formData = FormData.fromMap({
          'file': await MultipartFile.fromFile(file.path, filename: fileName),
        });

        await dio.post(
          'http://$serverIp/upload',
          data: formData,
          options: Options(headers: {'X-Local-Token': serverToken}),
          onSendProgress: (sent, total) {
            setState(() {
              uploadProgress = sent / total;
            });
          },
        );

        setState(() {
          uploadStatus = '';
          uploadProgress = 0.0;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$fileName uploaded successfully!')),
        );

        _loadFiles();
      }
    } catch (e) {
      setState(() {
        uploadStatus = '';
        uploadProgress = 0.0;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Upload failed: $e')));
    }
  }

  Future<void> _downloadFile(FileItem file) async {
    if (serverIp == null || serverToken == null) return;

    try {
      final dir = await getExternalStorageDirectory();
      final savePath = '${dir!.path}/${file.name}';

      setState(() {
        uploadStatus = 'Downloading ${file.name}...';
        uploadProgress = 0.0;
      });

      await dio.download(
        'http://$serverIp/download/${file.name}',
        savePath,
        options: Options(headers: {'X-Local-Token': serverToken}),
        onReceiveProgress: (received, total) {
          if (total != -1) {
            setState(() {
              uploadProgress = received / total;
            });
          }
        },
      );

      setState(() {
        uploadStatus = '';
        uploadProgress = 0.0;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${file.name} downloaded to Downloads folder')),
      );
    } catch (e) {
      setState(() {
        uploadStatus = '';
        uploadProgress = 0.0;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Download failed: $e')));
    }
  }

  Future<void> _deleteFile(FileItem file) async {
    if (serverIp == null || serverToken == null) return;

    try {
      await dio.delete(
        'http://$serverIp/delete/${file.name}',
        options: Options(headers: {'X-Local-Token': serverToken}),
      );

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('${file.name} deleted')));

      _loadFiles();
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Delete failed: $e')));
    }
  }

  void _disconnect() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('local_server_ip');
    await prefs.remove('local_server_token');

    setState(() {
      serverIp = null;
      serverToken = null;
      isConnected = false;
      files = [];
    });
  }

  @override
  Widget build(BuildContext context) {
    if (isScanning) {
      scannerController ??= MobileScannerController();

      return Scaffold(
        appBar: AppBar(
          title: const Text('Scan QR Code'),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () {
              setState(() => isScanning = false);
              scannerController?.stop();
            },
          ),
        ),
        body: MobileScanner(
          controller: scannerController,
          onDetect: _handleQRDetection,
        ),
      );
    }

    if (!isConnected) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.folder_shared, size: 100, color: Colors.blue),
                const SizedBox(height: 24),
                const Text(
                  'Local File Sharing',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Share files with your PC over LAN\nNo internet required!',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 16, color: Colors.grey),
                ),
                const SizedBox(height: 40),
                ElevatedButton.icon(
                  onPressed: () {
                    setState(() {
                      isScanning = true;
                      scannerController = MobileScannerController();
                    });
                  },
                  icon: const Icon(Icons.qr_code_scanner, size: 28),
                  label: const Text(
                    'Scan QR Code',
                    style: TextStyle(fontSize: 18),
                  ),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 16,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Open System Monitor on your PC\nand scan the QR code',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _loadFiles,
        child: Column(
          children: [
            // Connection info card
            Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blue.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.wifi, color: Colors.blue),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Connected to PC',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text(
                          serverIp ?? '',
                          style: const TextStyle(
                            fontSize: 12,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.red),
                    onPressed: _disconnect,
                  ),
                ],
              ),
            ),

            // Upload progress
            if (uploadStatus.isNotEmpty)
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Text(uploadStatus),
                    const SizedBox(height: 8),
                    LinearProgressIndicator(value: uploadProgress),
                  ],
                ),
              ),

            // File list
            Expanded(
              child: isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : files.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.folder_open, size: 64, color: Colors.grey),
                          SizedBox(height: 16),
                          Text(
                            'No files shared yet',
                            style: TextStyle(fontSize: 16, color: Colors.grey),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      itemCount: files.length,
                      itemBuilder: (context, index) {
                        final file = files[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 4,
                          ),
                          child: ListTile(
                            leading: Icon(_getFileIcon(file.name), size: 36),
                            title: Text(file.name),
                            subtitle: Text(_formatFileSize(file.size)),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: const Icon(
                                    Icons.download,
                                    color: Colors.blue,
                                  ),
                                  onPressed: () => _downloadFile(file),
                                ),
                                IconButton(
                                  icon: const Icon(
                                    Icons.delete,
                                    color: Colors.red,
                                  ),
                                  onPressed: () {
                                    showDialog(
                                      context: context,
                                      builder: (ctx) => AlertDialog(
                                        title: const Text('Delete File'),
                                        content: Text('Delete ${file.name}?'),
                                        actions: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(ctx),
                                            child: const Text('Cancel'),
                                          ),
                                          TextButton(
                                            onPressed: () {
                                              Navigator.pop(ctx);
                                              _deleteFile(file);
                                            },
                                            child: const Text(
                                              'Delete',
                                              style: TextStyle(
                                                color: Colors.red,
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    );
                                  },
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
      floatingActionButton: isConnected
          ? FloatingActionButton.extended(
              onPressed: _uploadFile,
              icon: const Icon(Icons.upload_file),
              label: const Text('Upload File'),
            )
          : null,
    );
  }

  IconData _getFileIcon(String filename) {
    final ext = filename.split('.').last.toLowerCase();
    switch (ext) {
      case 'pdf':
        return Icons.picture_as_pdf;
      case 'doc':
      case 'docx':
        return Icons.description;
      case 'xls':
      case 'xlsx':
        return Icons.table_chart;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return Icons.image;
      case 'mp4':
      case 'avi':
      case 'mkv':
        return Icons.video_file;
      case 'mp3':
        return Icons.audio_file;
      case 'zip':
      case 'rar':
      case '7z':
        return Icons.folder_zip;
      default:
        return Icons.insert_drive_file;
    }
  }

  String _formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024)
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }
}

class FileItem {
  final String name;
  final int size;
  final double modified;

  FileItem({required this.name, required this.size, required this.modified});

  factory FileItem.fromJson(Map<String, dynamic> json) {
    return FileItem(
      name: json['name'],
      size: json['size'],
      modified: json['modified'].toDouble(),
    );
  }
}
