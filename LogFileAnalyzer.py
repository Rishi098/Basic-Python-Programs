"""
Log File Analyzer
==================
A comprehensive tool to parse and analyze log files with various statistics and insights.

Features:
- Count total number of log entries
- Analyze log levels (INFO, WARNING, ERROR, DEBUG, CRITICAL)
- Find most frequent error messages
- Identify top IP addresses (if present in logs)
- Extract timestamp information and analyze time patterns
- Export analysis results to a text file

Author: Your Name
Date: 2025
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
import os


class LogAnalyzer:
    """
    A class to analyze log files and extract meaningful insights.
    
    Attributes:
        log_file (str): Path to the log file to analyze
        log_entries (list): List of all log lines
        log_levels (Counter): Count of each log level
        error_messages (list): List of all error messages
        timestamps (list): List of all timestamps found in logs
        ip_addresses (list): List of all IP addresses found in logs
    """
    
    def __init__(self, log_file):
        """
        Initialize the LogAnalyzer with a log file path.
        
        Args:
            log_file (str): Path to the log file to be analyzed
        """
        self.log_file = log_file
        self.log_entries = []
        self.log_levels = Counter()
        self.error_messages = []
        self.timestamps = []
        self.ip_addresses = []
        
    def read_log_file(self):
        """
        Read the log file and store all entries.
        
        Returns:
            bool: True if file read successfully, False otherwise
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as file:
                self.log_entries = file.readlines()
            print(f"✓ Successfully read {len(self.log_entries)} log entries")
            return True
        except FileNotFoundError:
            print(f"✗ Error: File '{self.log_file}' not found!")
            return False
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            return False
    
    def parse_log_levels(self):
        """
        Parse and count different log levels (INFO, WARNING, ERROR, DEBUG, CRITICAL).
        
        Uses regex to find log level keywords in each log entry.
        """
        # Common log level patterns
        level_pattern = r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|WARN|FATAL)\b'
        
        for entry in self.log_entries:
            match = re.search(level_pattern, entry, re.IGNORECASE)
            if match:
                level = match.group(1).upper()
                # Normalize WARN to WARNING and FATAL to CRITICAL
                if level == 'WARN':
                    level = 'WARNING'
                elif level == 'FATAL':
                    level = 'CRITICAL'
                self.log_levels[level] += 1
    
    def extract_error_messages(self):
        """
        Extract all error and critical messages from the log file.
        
        Identifies lines containing ERROR or CRITICAL levels and stores them.
        """
        error_pattern = r'.*(ERROR|CRITICAL|FATAL).*'
        
        for entry in self.log_entries:
            if re.search(error_pattern, entry, re.IGNORECASE):
                self.error_messages.append(entry.strip())
    
    def extract_timestamps(self):
        """
        Extract timestamps from log entries.
        
        Supports multiple timestamp formats:
        - YYYY-MM-DD HH:MM:SS
        - DD/MM/YYYY HH:MM:SS
        - MM-DD-YYYY HH:MM:SS
        """
        # Common timestamp patterns
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # 2025-01-15 10:30:45
            r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}',  # 15/01/2025 10:30:45
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2}',  # 01-15-2025 10:30:45
        ]
        
        for entry in self.log_entries:
            for pattern in timestamp_patterns:
                match = re.search(pattern, entry)
                if match:
                    self.timestamps.append(match.group(0))
                    break
    
    def extract_ip_addresses(self):
        """
        Extract IP addresses from log entries.
        
        Uses regex to find IPv4 addresses in the format XXX.XXX.XXX.XXX
        """
        # IPv4 pattern
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        
        for entry in self.log_entries:
            matches = re.findall(ip_pattern, entry)
            self.ip_addresses.extend(matches)
    
    def analyze_time_patterns(self):
        """
        Analyze when most logs occur (by hour of day).
        
        Returns:
            Counter: Count of log entries for each hour of the day
        """
        hour_counter = Counter()
        
        for timestamp in self.timestamps:
            try:
                # Try different datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m-%d-%Y %H:%M:%S']:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        hour_counter[dt.hour] += 1
                        break
                    except ValueError:
                        continue
            except Exception:
                continue
        
        return hour_counter
    
    def generate_report(self):
        """
        Generate a comprehensive analysis report.
        
        Returns:
            str: Formatted report string with all analysis results
        """
        report = []
        report.append("=" * 60)
        report.append("LOG FILE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"\nLog File: {self.log_file}")
        report.append(f"Total Log Entries: {len(self.log_entries)}\n")
        
        # Log Level Distribution
        report.append("-" * 60)
        report.append("LOG LEVEL DISTRIBUTION")
        report.append("-" * 60)
        if self.log_levels:
            for level, count in self.log_levels.most_common():
                percentage = (count / len(self.log_entries)) * 100
                report.append(f"{level:12} : {count:6} ({percentage:5.2f}%)")
        else:
            report.append("No log levels found")
        
        # Error Summary
        report.append("\n" + "-" * 60)
        report.append("ERROR SUMMARY")
        report.append("-" * 60)
        error_count = self.log_levels.get('ERROR', 0) + self.log_levels.get('CRITICAL', 0)
        report.append(f"Total Errors/Critical: {error_count}")
        
        if self.error_messages:
            report.append(f"\nTop 5 Error Messages:")
            error_counter = Counter(self.error_messages)
            for i, (error, count) in enumerate(error_counter.most_common(5), 1):
                report.append(f"\n{i}. ({count}x) {error[:100]}...")
        
        # IP Address Analysis
        report.append("\n" + "-" * 60)
        report.append("IP ADDRESS ANALYSIS")
        report.append("-" * 60)
        if self.ip_addresses:
            ip_counter = Counter(self.ip_addresses)
            report.append(f"Unique IP Addresses: {len(ip_counter)}")
            report.append(f"\nTop 10 Most Frequent IPs:")
            for i, (ip, count) in enumerate(ip_counter.most_common(10), 1):
                report.append(f"{i:2}. {ip:15} - {count} occurrences")
        else:
            report.append("No IP addresses found")
        
        # Time Pattern Analysis
        report.append("\n" + "-" * 60)
        report.append("TIME PATTERN ANALYSIS")
        report.append("-" * 60)
        if self.timestamps:
            hour_counter = self.analyze_time_patterns()
            report.append(f"Total Timestamps Found: {len(self.timestamps)}")
            if hour_counter:
                report.append("\nLog Activity by Hour:")
                for hour in sorted(hour_counter.keys()):
                    count = hour_counter[hour]
                    bar = '█' * (count // max(1, max(hour_counter.values()) // 50))
                    report.append(f"{hour:02d}:00 - {count:4} {bar}")
        else:
            report.append("No timestamps found")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def analyze(self):
        """
        Main method to perform complete log analysis.
        
        Executes all analysis methods and generates a report.
        
        Returns:
            str: Complete analysis report
        """
        print("\n🔍 Starting Log File Analysis...")
        print("-" * 60)
        
        # Read the log file
        if not self.read_log_file():
            return None
        
        # Perform all analyses
        print("📊 Parsing log levels...")
        self.parse_log_levels()
        
        print("❌ Extracting error messages...")
        self.extract_error_messages()
        
        print("🕒 Extracting timestamps...")
        self.extract_timestamps()
        
        print("🌐 Extracting IP addresses...")
        self.extract_ip_addresses()
        
        print("✓ Analysis complete!\n")
        
        # Generate and return report
        return self.generate_report()
    
    def save_report(self, output_file="log_analysis_report.txt"):
        """
        Save the analysis report to a file.
        
        Args:
            output_file (str): Name of the output file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        report = self.generate_report()
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(report)
            print(f"✓ Report saved to '{output_file}'")
            return True
        except Exception as e:
            print(f"✗ Error saving report: {e}")
            return False


def create_sample_log(filename="sample.log"):
    """
    Create a sample log file for demonstration purposes.
    
    Args:
        filename (str): Name of the sample log file to create
    """
    sample_logs = [
        "2025-01-15 10:30:45 INFO [192.168.1.100] User login successful",
        "2025-01-15 10:31:12 WARNING [192.168.1.101] High memory usage detected",
        "2025-01-15 10:32:30 ERROR [192.168.1.102] Database connection failed",
        "2025-01-15 10:33:45 INFO [192.168.1.100] File uploaded successfully",
        "2025-01-15 10:35:20 CRITICAL [192.168.1.103] System out of memory",
        "2025-01-15 10:36:10 DEBUG [192.168.1.100] Debug mode enabled",
        "2025-01-15 10:37:55 ERROR [192.168.1.102] Database connection failed",
        "2025-01-15 10:38:30 INFO [192.168.1.104] User logout",
        "2025-01-15 11:30:45 WARNING [192.168.1.101] CPU usage above 80%",
        "2025-01-15 11:32:15 ERROR [192.168.1.105] API request timeout",
        "2025-01-15 12:15:30 INFO [192.168.1.100] Scheduled backup started",
        "2025-01-15 12:45:30 INFO [192.168.1.100] Scheduled backup completed",
        "2025-01-15 14:20:10 ERROR [192.168.1.102] Database connection failed",
        "2025-01-15 15:10:45 WARNING [192.168.1.106] Disk space low",
        "2025-01-15 16:05:20 INFO [192.168.1.107] Service restarted",
    ]
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("\n".join(sample_logs))
    print(f"✓ Sample log file '{filename}' created")


def main():
    """
    Main function to demonstrate the Log Analyzer.
    """
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           LOG FILE ANALYZER                                ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Get log file path from user
    log_file = input("Enter the path to your log file (or press Enter for sample): ").strip()
    
    # Create sample log if no file specified
    if not log_file:
        create_sample_log()
        log_file = "sample.log"
    
    # Check if file exists
    if not os.path.exists(log_file):
        print(f"\n✗ File '{log_file}' not found!")
        create_sample = input("Would you like to create a sample log file? (y/n): ").lower()
        if create_sample == 'y':
            create_sample_log()
            log_file = "sample.log"
        else:
            return
    
    # Analyze the log file
    analyzer = LogAnalyzer(log_file)
    report = analyzer.analyze()
    
    if report:
        print(report)
        
        # Ask if user wants to save the report
        save_option = input("\nWould you like to save this report? (y/n): ").lower()
        if save_option == 'y':
            output_filename = input("Enter output filename (default: log_analysis_report.txt): ").strip()
            if not output_filename:
                output_filename = "log_analysis_report.txt"
            analyzer.save_report(output_filename)


if __name__ == "__main__":
    main()