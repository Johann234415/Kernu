from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import threading
import configparser
import os
import time
import json
import asyncio
import aiohttp
import requests
from typing import Dict, List
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Global variables to store bot instance and data
bot_instance = None
active_operations = {}

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

# Enhanced Dashboard HTML template with more features
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KER.NU Ultimate Control Center</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Courier+Prime&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Orbitron', monospace;
            background: linear-gradient(135deg, #000000 0%, #1a0033 50%, #000000 100%);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 1px,
                    rgba(255,255,255,0.02) 2px,
                    rgba(255,255,255,0.02) 4px
                ),
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 1px,
                    rgba(255,255,255,0.02) 2px,
                    rgba(255,255,255,0.02) 4px
                );
            pointer-events: none;
            z-index: 1;
        }

        .matrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(0,255,255,0.1) 0%, transparent 70%),
                        radial-gradient(circle at 80% 50%, rgba(255,0,255,0.1) 0%, transparent 70%);
            animation: matrix-pulse 6s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        @keyframes matrix-pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.8; }
        }

        @keyframes cyber-glitch {
            0% { transform: translate(0); filter: hue-rotate(0deg); }
            10% { transform: translate(-2px, 2px); filter: hue-rotate(90deg); }
            20% { transform: translate(-2px, -2px); filter: hue-rotate(180deg); }
            30% { transform: translate(2px, 2px); filter: hue-rotate(270deg); }
            40% { transform: translate(2px, -2px); filter: hue-rotate(360deg); }
            50% { transform: translate(-2px, 2px); filter: hue-rotate(450deg); }
            60% { transform: translate(-2px, -2px); filter: hue-rotate(540deg); }
            70% { transform: translate(2px, 2px); filter: hue-rotate(630deg); }
            80% { transform: translate(2px, -2px); filter: hue-rotate(720deg); }
            90% { transform: translate(-2px, 2px); filter: hue-rotate(810deg); }
            100% { transform: translate(0); filter: hue-rotate(900deg); }
        }

        .header {
            background: linear-gradient(135deg, #000000 0%, #330066 50%, #000000 100%);
            padding: 30px;
            text-align: center;
            border-bottom: 3px solid #00ffff;
            position: relative;
            z-index: 10;
            box-shadow: 0 10px 30px rgba(0,255,255,0.3);
        }

        .header h1 {
            font-size: 4em;
            font-weight: 900;
            margin-bottom: 15px;
            background: linear-gradient(45deg, #00ffff, #ff00ff, #ffff00, #00ff00);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: cyber-glitch 3s infinite, gradient-flow 4s ease-in-out infinite;
            letter-spacing: 4px;
            text-shadow: 0 0 20px rgba(0,255,255,0.8);
        }

        @keyframes gradient-flow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
            position: relative;
            z-index: 10;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        .stats-panel {
            background: linear-gradient(135deg, #000033 0%, #330066 50%, #000033 100%);
            border: 2px solid #00ffff;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 0 30px rgba(0,255,255,0.3);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .stat-card {
            background: linear-gradient(135deg, #000000 0%, #1a1a2e 50%, #000000 100%);
            border: 1px solid #00ffff;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0,255,255,0.5);
        }

        .stat-card h3 {
            font-size: 1.2em;
            margin-bottom: 10px;
            color: #00ffff;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 0 0 15px #00ffff;
            animation: stat-pulse 2s infinite;
        }

        @keyframes stat-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .control-center {
            background: linear-gradient(135deg, #000033 0%, #330066 50%, #000033 100%);
            border: 2px solid #00ffff;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 0 30px rgba(0,255,255,0.3);
        }

        .control-tabs {
            display: flex;
            margin-bottom: 25px;
            border-bottom: 1px solid #00ffff;
        }

        .tab-button {
            background: transparent;
            border: none;
            color: #ffffff;
            padding: 15px 25px;
            cursor: pointer;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .tab-button.active {
            color: #00ffff;
            border-bottom-color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .command-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .cmd-btn {
            background: linear-gradient(135deg, #001122 0%, #002244 50%, #001122 100%);
            border: 2px solid #00ffff;
            color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            font-size: 0.9em;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .cmd-btn:hover {
            background: linear-gradient(135deg, #00ffff 0%, #0099cc 50%, #00ffff 100%);
            color: #000000;
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,255,255,0.4);
        }

        .cmd-btn.danger {
            border-color: #ff0040;
            background: linear-gradient(135deg, #220011 0%, #440022 50%, #220011 100%);
        }

        .cmd-btn.danger:hover {
            background: linear-gradient(135deg, #ff0040 0%, #cc0033 50%, #ff0040 100%);
        }

        .cmd-btn.warning {
            border-color: #ffaa00;
            background: linear-gradient(135deg, #221100 0%, #442200 50%, #221100 100%);
        }

        .cmd-btn.warning:hover {
            background: linear-gradient(135deg, #ffaa00 0%, #cc8800 50%, #ffaa00 100%);
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }

        .cyber-input {
            flex: 1;
            background: #000000;
            border: 2px solid #00ffff;
            border-radius: 5px;
            padding: 12px;
            color: #ffffff;
            font-family: 'Courier Prime', monospace;
            font-size: 1em;
        }

        .cyber-input:focus {
            outline: none;
            box-shadow: 0 0 15px rgba(0,255,255,0.5);
        }

        .server-list {
            max-height: 300px;
            overflow-y: auto;
            background: #000000;
            border: 2px solid #00ffff;
            border-radius: 5px;
            padding: 15px;
        }

        .server-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #333;
            margin-bottom: 10px;
        }

        .server-info {
            flex: 1;
        }

        .server-name {
            font-weight: bold;
            color: #00ffff;
        }

        .server-details {
            font-size: 0.8em;
            color: #cccccc;
        }

        .server-actions {
            display: flex;
            gap: 10px;
        }

        .action-btn {
            background: #330066;
            border: 1px solid #00ffff;
            color: #ffffff;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
        }

        .console-panel {
            background: linear-gradient(135deg, #000000 0%, #1a0033 50%, #000000 100%);
            border: 2px solid #00ffff;
            border-radius: 10px;
            padding: 25px;
            margin-top: 30px;
            box-shadow: 0 0 30px rgba(0,255,255,0.3);
        }

        .console-output {
            background: #000000;
            border: 2px solid #00ffff;
            border-radius: 5px;
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier Prime', monospace;
            font-size: 0.9em;
            color: #00ff00;
            text-shadow: 0 0 5px #00ff00;
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #000033 0%, #330066 100%);
            border: 2px solid #00ffff;
            color: #ffffff;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,255,255,0.5);
            z-index: 1000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }

        .notification.show {
            transform: translateX(0);
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #000000;
            border: 1px solid #00ffff;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ffff, #ff00ff);
            width: 0%;
            transition: width 0.3s ease;
            position: relative;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: progress-shine 2s infinite;
        }

        @keyframes progress-shine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }

        .modal.show {
            display: flex;
        }

        .modal-content {
            background: linear-gradient(135deg, #000033 0%, #330066 100%);
            border: 2px solid #00ffff;
            border-radius: 10px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 0 50px rgba(0,255,255,0.5);
        }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }

            .command-grid {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 2.5em;
            }
        }
    </style>
</head>
<body>
    <div class="matrix-bg"></div>

    <div class="header">
        <h1>🔥 KER.NU ULTIMATE CONTROL CENTER</h1>
        <p>🏢 Publisher: Kernu Inc. | Cyber Warfare Division</p>
        <div style="margin-top: 15px;">
            <span class="status online">🟢 MAINFRAME ONLINE</span>
            <span style="margin-left: 20px; color: #00ffff;">Last Update: <span id="lastUpdate">{{ last_update }}</span></span>
        </div>
    </div>

    <div class="container">
        <div class="dashboard-grid">
            <div class="stats-panel">
                <h2 style="color: #00ffff; margin-bottom: 20px; text-align: center;">📊 SYSTEM STATUS</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>🌐 Servers</h3>
                        <div class="stat-value" id="totalServers">{{ stats.total_servers }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>👥 Users</h3>
                        <div class="stat-value" id="totalUsers">{{ stats.total_users }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>💥 Nuked</h3>
                        <div class="stat-value" id="nukedServers">{{ stats.nuked_servers }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>⚡ Uptime</h3>
                        <div class="stat-value" id="uptime">{{ stats.uptime }}</div>
                    </div>
                </div>

                <div style="margin-top: 25px;">
                    <h3 style="color: #00ffff; margin-bottom: 15px;">🎯 Active Operations</h3>
                    <div id="activeOperations" style="color: #cccccc; min-height: 50px;">
                        No active operations
                    </div>
                </div>
            </div>

            <div class="control-center">
                <div class="control-tabs">
                    <button class="tab-button active" onclick="switchTab('commands')">🎮 Commands</button>
                    <button class="tab-button" onclick="switchTab('servers')">🌐 Servers</button>
                    <button class="tab-button" onclick="switchTab('users')">👥 Users</button>
                    <button class="tab-button" onclick="switchTab('economy')">💰 Economy</button>
                </div>

                <div id="commands" class="tab-content active">
                    <h3 style="color: #00ffff; margin-bottom: 20px;">💀 DESTRUCTION PROTOCOLS</h3>
                    <div class="command-grid">
                        <button class="cmd-btn danger" onclick="executeCommand('nuke_all')">💀 NUKE ALL SERVERS</button>
                        <button class="cmd-btn danger" onclick="executeCommand('mass_ban')">🔨 MASS BAN HAMMER</button>
                        <button class="cmd-btn warning" onclick="executeCommand('mass_dm')">📬 MASS DM BLAST</button>
                        <button class="cmd-btn" onclick="executeCommand('global_webhook')">🎯 GLOBAL WEBHOOK</button>
                        <button class="cmd-btn warning" onclick="executeCommand('server_raid')">🏴‍☠️ SERVER RAID</button>
                        <button class="cmd-btn danger" onclick="executeCommand('emergency_stop')">🚨 EMERGENCY STOP</button>
                    </div>

                    <div style="margin-top: 25px;">
                        <h4 style="color: #00ffff; margin-bottom: 15px;">🎯 Targeted Operations</h4>
                        <div class="input-group">
                            <input type="text" id="targetServer" class="cyber-input" placeholder="Server ID">
                            <button class="cmd-btn" onclick="nukeSpecificServer()">💥 NUKE SERVER</button>
                        </div>
                        <div class="input-group">
                            <input type="text" id="targetUser" class="cyber-input" placeholder="User ID">
                            <button class="cmd-btn warning" onclick="banUser()">🔨 BAN USER</button>
                        </div>
                    </div>
                </div>

                <div id="servers" class="tab-content">
                    <h3 style="color: #00ffff; margin-bottom: 20px;">🌐 SERVER MANAGEMENT</h3>
                    <button class="cmd-btn" onclick="refreshServerList()" style="margin-bottom: 15px;">🔄 REFRESH LIST</button>
                    <div id="serverList" class="server-list">
                        Loading servers...
                    </div>
                </div>

                <div id="users" class="tab-content">
                    <h3 style="color: #00ffff; margin-bottom: 20px;">👥 USER MANAGEMENT</h3>
                    <div class="input-group">
                        <input type="text" id="searchUser" class="cyber-input" placeholder="Search User ID or Name">
                        <button class="cmd-btn" onclick="searchUser()">🔍 SEARCH</button>
                    </div>
                    <div id="userResults" style="margin-top: 20px; min-height: 200px; background: #000; border: 2px solid #00ffff; padding: 15px; border-radius: 5px;">
                        Enter a user ID to search
                    </div>
                </div>

                <div id="economy" class="tab-content">
                    <h3 style="color: #00ffff; margin-bottom: 20px;">💰 ECONOMY CONTROL</h3>
                    <div class="command-grid">
                        <button class="cmd-btn" onclick="showCoinBombModal()">💣 COIN BOMB</button>
                        <button class="cmd-btn warning" onclick="executeCommand('money_rain')">💸 MONEY RAIN</button>
                        <button class="cmd-btn" onclick="executeCommand('reset_economy')">🔄 RESET ECONOMY</button>
                        <button class="cmd-btn" onclick="generateLotteryWinner()">🎰 FORCE LOTTERY WIN</button>
                    </div>

                    <div style="margin-top: 25px;">
                        <h4 style="color: #00ffff; margin-bottom: 15px;">📊 Economy Stats</h4>
                        <div id="economyStats" style="background: #000; border: 2px solid #00ffff; padding: 15px; border-radius: 5px;">
                            <div>Total Coins in Circulation: <span id="totalCoins">Loading...</span></div>
                            <div>Richest User: <span id="richestUser">Loading...</span></div>
                            <div>Total Transactions: <span id="totalTransactions">Loading...</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="console-panel">
            <h2 style="color: #00ffff; margin-bottom: 20px;">💻 COMMAND CONSOLE</h2>
            <div class="input-group">
                <input type="text" id="consoleInput" class="cyber-input" placeholder="Enter console command..." onkeypress="if(event.key==='Enter') sendConsoleCommand()">
                <button class="cmd-btn" onclick="sendConsoleCommand()">⚡ EXECUTE</button>
                <button class="cmd-btn warning" onclick="clearConsole()">🗑️ CLEAR</button>
            </div>
            <div id="consoleOutput" class="console-output">
KER.NU CYBER WARFARE CONSOLE v3.0
=====================================
[SYSTEM] Mainframe initialized
[SYSTEM] All systems operational
[READY] Awaiting commands...

            </div>
        </div>
    </div>

    <!-- Coin Bomb Modal -->
    <div id="coinBombModal" class="modal">
        <div class="modal-content">
            <h3 style="color: #00ffff; margin-bottom: 20px;">💣 COIN BOMB DEPLOYMENT</h3>
            <div class="input-group">
                <input type="text" id="coinBombUser" class="cyber-input" placeholder="Target User ID">
            </div>
            <div class="input-group">
                <input type="number" id="coinBombAmount" class="cyber-input" placeholder="Coin Amount">
            </div>
            <div style="margin-top: 20px; display: flex; gap: 15px;">
                <button class="cmd-btn" onclick="deployCoinBomb()">💣 DEPLOY</button>
                <button class="cmd-btn warning" onclick="closeCoinBombModal()">❌ CANCEL</button>
            </div>
        </div>
    </div>

    <!-- Notification Container -->
    <div id="notification" class="notification"></div>

    <script>
        let currentTab = 'commands';
        let operationInProgress = false;

        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            currentTab = tabName;

            // Load tab-specific data
            if (tabName === 'servers') {
                refreshServerList();
            } else if (tabName === 'economy') {
                loadEconomyStats();
            }
        }

        function executeCommand(command) {
            if (operationInProgress) {
                showNotification('⚠️ Operation in progress, please wait...', 'warning');
                return;
            }

            operationInProgress = true;
            showNotification('🚀 Executing command: ' + command, 'info');
            updateConsole('[EXECUTING] Command: ' + command);

            fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    timestamp: Date.now()
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('✅ ' + data.message, 'success');
                    updateConsole('[SUCCESS] ' + data.message);
                    if (data.details) {
                        updateConsole('[DETAILS] ' + data.details);
                    }
                } else {
                    showNotification('❌ ' + data.message, 'error');
                    updateConsole('[ERROR] ' + data.message);
                }
                operationInProgress = false;
            })
            .catch(error => {
                showNotification('❌ Network error: ' + error.message, 'error');
                updateConsole('[ERROR] Network error: ' + error.message);
                operationInProgress = false;
            });
        }

        function nukeSpecificServer() {
            const serverId = document.getElementById('targetServer').value.trim();
            if (!serverId) {
                showNotification('⚠️ Please enter a server ID', 'warning');
                return;
            }

            if (confirm('💀 Are you sure you want to NUKE server ' + serverId + '?')) {
                executeCommand('nuke_server:' + serverId);
                document.getElementById('targetServer').value = '';
            }
        }

        function banUser() {
            const userId = document.getElementById('targetUser').value.trim();
            if (!userId) {
                showNotification('⚠️ Please enter a user ID', 'warning');
                return;
            }

            if (confirm('🔨 Are you sure you want to BAN user ' + userId + ' from all servers?')) {
                executeCommand('ban_user:' + userId);
                document.getElementById('targetUser').value = '';
            }
        }

        function refreshServerList() {
            document.getElementById('serverList').innerHTML = '<div style="text-align: center; color: #00ffff;">🔄 Loading servers...</div>';

            fetch('/api/servers')
            .then(response => response.json())
            .then(data => {
                let html = '';
                if (data.servers && data.servers.length > 0) {
                    data.servers.forEach(server => {
                        html += `
                            <div class="server-item">
                                <div class="server-info">
                                    <div class="server-name">${server.name}</div>
                                    <div class="server-details">ID: ${server.id} | Members: ${server.member_count} | Owner: ${server.owner}</div>
                                </div>
                                <div class="server-actions">
                                    <button class="action-btn" onclick="nukeServer('${server.id}')">💥 Nuke</button>
                                    <button class="action-btn" onclick="spyServer('${server.id}')">🕵️ Spy</button>
                                    <button class="action-btn" onclick="leaveServer('${server.id}')">🚪 Leave</button>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    html = '<div style="text-align: center; color: #cccccc;">No servers found</div>';
                }
                document.getElementById('serverList').innerHTML = html;
            })
            .catch(error => {
                document.getElementById('serverList').innerHTML = '<div style="text-align: center; color: #ff0040;">Error loading servers</div>';
            });
        }

        function nukeServer(serverId) {
            if (confirm('💀 Nuke server ' + serverId + '?')) {
                executeCommand('nuke_server:' + serverId);
            }
        }

        function spyServer(serverId) {
            executeCommand('spy_server:' + serverId);
        }

        function leaveServer(serverId) {
            if (confirm('🚪 Leave server ' + serverId + '?')) {
                executeCommand('leave_server:' + serverId);
            }
        }

        function searchUser() {
            const userId = document.getElementById('searchUser').value.trim();
            if (!userId) {
                showNotification('⚠️ Please enter a user ID', 'warning');
                return;
            }

            document.getElementById('userResults').innerHTML = '<div style="text-align: center; color: #00ffff;">🔍 Searching...</div>';

            fetch('/api/user/' + userId)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const user = data.user;
                    const html = `
                        <div style="color: #00ffff; font-weight: bold; margin-bottom: 15px;">User Information</div>
                        <div><strong>Name:</strong> ${user.name}</div>
                        <div><strong>ID:</strong> ${user.id}</div>
                        <div><strong>Coins:</strong> ${user.coins}</div>
                        <div><strong>Nuked Servers:</strong> ${user.nuked_servers}</div>
                        <div><strong>Nuked Members:</strong> ${user.nuked_members}</div>
                        <div><strong>Level:</strong> ${user.level}</div>
                        <div><strong>XP:</strong> ${user.xp}</div>
                        <div style="margin-top: 15px;">
                            <button class="action-btn" onclick="banUser('${user.id}')">🔨 Ban</button>
                            <button class="action-btn" onclick="coinBombUser('${user.id}')">💣 Coin Bomb</button>
                        </div>
                    `;
                    document.getElementById('userResults').innerHTML = html;
                } else {
                    document.getElementById('userResults').innerHTML = '<div style="color: #ff0040;">User not found</div>';
                }
            })
            .catch(error => {
                document.getElementById('userResults').innerHTML = '<div style="color: #ff0040;">Error searching user</div>';
            });
        }

        function loadEconomyStats() {
            fetch('/api/economy')
            .then(response => response.json())
            .then(data => {
                document.getElementById('totalCoins').textContent = data.total_coins.toLocaleString();
                document.getElementById('richestUser').textContent = data.richest_user;
                document.getElementById('totalTransactions').textContent = data.total_transactions.toLocaleString();
            })
            .catch(error => {
                updateConsole('[ERROR] Failed to load economy stats');
            });
        }

        function showCoinBombModal() {
            document.getElementById('coinBombModal').classList.add('show');
        }

        function closeCoinBombModal() {
            document.getElementById('coinBombModal').classList.remove('show');
            document.getElementById('coinBombUser').value = '';
            document.getElementById('coinBombAmount').value = '';
        }

        function deployCoinBomb() {
            const userId = document.getElementById('coinBombUser').value.trim();
            const amount = document.getElementById('coinBombAmount').value.trim();

            if (!userId || !amount) {
                showNotification('⚠️ Please fill all fields', 'warning');
                return;
            }

            if (amount < 1 || amount > 1000000) {
                showNotification('⚠️ Amount must be between 1 and 1,000,000', 'warning');
                return;
            }

            executeCommand('coin_bomb:' + userId + ':' + amount);
            closeCoinBombModal();
        }

        function generateLotteryWinner() {
            if (confirm('🎰 Force generate a lottery winner?')) {
                executeCommand('force_lottery');
            }
        }

        function sendConsoleCommand() {
            const input = document.getElementById('consoleInput');
            const command = input.value.trim();

            if (command) {
                updateConsole('[INPUT] ' + command);

                fetch('/console', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({command: command})
                })
                .then(response => response.json())
                .then(data => {
                    updateConsole('[OUTPUT] ' + data.result);
                    input.value = '';
                })
                .catch(error => {
                    updateConsole('[ERROR] Console error: ' + error.message);
                });
            }
        }

        function clearConsole() {
            document.getElementById('consoleOutput').innerHTML = `
KER.NU CYBER WARFARE CONSOLE v3.0
=====================================
[SYSTEM] Console cleared
[READY] Awaiting commands...

            `;
        }

        function updateConsole(text) {
            const output = document.getElementById('consoleOutput');
            const timestamp = new Date().toLocaleTimeString();
            output.innerHTML += `[${timestamp}] ${text}\n`;
            output.scrollTop = output.scrollHeight;
        }

        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = 'notification show';

            setTimeout(() => {
                notification.classList.remove('show');
            }, 4000);
        }

        // Auto-refresh stats every 15 seconds
        setInterval(() => {
            fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('totalServers').textContent = data.total_servers;
                document.getElementById('totalUsers').textContent = data.total_users;
                document.getElementById('nukedServers').textContent = data.nuked_servers;
                document.getElementById('uptime').textContent = data.uptime;
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            })
            .catch(error => {
                updateConsole('[ERROR] Failed to refresh stats: ' + error.message);
            });
        }, 15000);

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshServerList();
            loadEconomyStats();
            updateConsole('[SYSTEM] Dashboard initialized successfully');
        });
    </script>
</body>
</html>
'''

def get_advanced_stats():
    """Get comprehensive bot statistics"""
    try:
        config = configparser.ConfigParser()
        config.read('database.ini')

        total_users = len([k for k in config.keys() if k != 'DEFAULT' and k != 'users' and k.isdigit()])
        total_nuked_servers = 0
        total_nuked_members = 0
        total_coins = 0

        for user in config.sections():
            if user != "users" and user.isdigit():
                total_nuked_servers += int(config.get(user, 'nuked_server', fallback=0))
                total_nuked_members += int(config.get(user, 'nuked_member', fallback=0))
                total_coins += int(config.get(user, 'coins', fallback=0))

        # Calculate uptime
        start_time = getattr(get_advanced_stats, 'start_time', time.time())
        if not hasattr(get_advanced_stats, 'start_time'):
            get_advanced_stats.start_time = start_time

        uptime_seconds = int(time.time() - start_time)
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        uptime = f"{uptime_hours}h {uptime_minutes}m"

        # Get server count from bot if available
        total_servers = 0
        if bot_instance:
            total_servers = len(bot_instance.guilds)

        return {
            'total_servers': total_servers,
            'total_users': total_users,
            'nuked_servers': total_nuked_servers,
            'nuked_members': total_nuked_members,
            'total_coins': total_coins,
            'uptime': uptime,
            'last_update': time.strftime('%H:%M:%S')
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return {
            'total_servers': 0,
            'total_users': 0,
            'nuked_servers': 0,
            'nuked_members': 0,
            'total_coins': 0,
            'uptime': '0h 0m',
            'last_update': time.strftime('%H:%M:%S')
        }

@app.route('/')
def dashboard():
    stats = get_advanced_stats()
    return render_template_string(DASHBOARD_HTML, stats=stats, last_update=time.strftime('%H:%M:%S'))

@app.route('/api/stats')
def stats_api():
    return jsonify(get_advanced_stats())

@app.route('/api/servers')
def servers_api():
    """Get list of all servers"""
    try:
        servers = []
        if bot_instance:
            # Get home server ID from config
            config = configparser.ConfigParser()
            config.read('config.ini')
            home_server_id = int(config.get('server', 'server_id', fallback=0))
            
            for guild in bot_instance.guilds:
                if guild.id != home_server_id:  # Exclude home server
                    servers.append({
                        'id': guild.id,
                        'name': guild.name,
                        'member_count': guild.member_count,
                        'owner': str(guild.owner) if guild.owner else 'Unknown',
                        'created_at': guild.created_at.strftime('%Y-%m-%d')
                    })

        return jsonify({'success': True, 'servers': servers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user/<user_id>')
def user_api(user_id):
    """Get user information"""
    try:
        config = configparser.ConfigParser()
        config.read('database.ini')

        if str(user_id) in config and str(user_id) != 'users':
            user_data = config[str(user_id)]

            # Try to get user from Discord
            user_name = f"User {user_id}"
            if bot_instance:
                try:
                    discord_user = bot_instance.get_user(int(user_id))
                    if discord_user:
                        user_name = discord_user.name
                except:
                    pass

            # Calculate level from XP
            xp = int(user_data.get('xp', 0))
            level = int((xp / 100) ** 0.5) + 1

            user_info = {
                'id': user_id,
                'name': user_name,
                'coins': int(user_data.get('coins', 0)),
                'nuked_servers': int(user_data.get('nuked_server', 0)),
                'nuked_members': int(user_data.get('nuked_member', 0)),
                'level': level,
                'xp': xp,
                'biggest_server': int(user_data.get('biggest_server', 0))
            }

            return jsonify({'success': True, 'user': user_info})
        else:
            return jsonify({'success': False, 'error': 'User not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/economy')
def economy_api():
    """Get economy statistics"""
    try:
        config = configparser.ConfigParser()
        config.read('database.ini')

        total_coins = 0
        richest_user = "None"
        richest_amount = 0
        total_transactions = 0

        for user in config.sections():
            if user != "users" and user.isdigit():
                coins = int(config.get(user, 'coins', fallback=0))
                total_coins += coins

                if coins > richest_amount:
                    richest_amount = coins
                    richest_user = f"User {user} ({coins:,} coins)"

                # Estimate transactions (this could be enhanced with actual tracking)
                total_transactions += int(config.get(user, 'nuked_server', fallback=0)) * 10

        return jsonify({
            'total_coins': total_coins,
            'richest_user': richest_user,
            'total_transactions': total_transactions
        })
    except Exception as e:
        return jsonify({
            'total_coins': 0,
            'richest_user': 'Error',
            'total_transactions': 0
        })

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute dashboard commands with real bot integration"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        timestamp = data.get('timestamp', time.time())

        # Store operation
        operation_id = hashlib.md5(f"{command}{timestamp}".encode()).hexdigest()[:8]
        active_operations[operation_id] = {
            'command': command,
            'status': 'executing',
            'timestamp': timestamp
        }

        # Parse command and arguments
        if ':' in command:
            cmd_parts = command.split(':')
            base_cmd = cmd_parts[0]
            args = cmd_parts[1:]
        else:
            base_cmd = command
            args = []

        # Execute commands based on type
        if base_cmd == 'nuke_all':
            return execute_nuke_all()
        elif base_cmd == 'nuke_server' and args:
            return execute_nuke_server(args[0])
        elif base_cmd == 'mass_ban':
            return execute_mass_ban()
        elif base_cmd == 'mass_dm':
            return execute_mass_dm()
        elif base_cmd == 'ban_user' and args:
            return execute_ban_user(args[0])
        elif base_cmd == 'coin_bomb' and len(args) >= 2:
            return execute_coin_bomb(args[0], args[1])
        elif base_cmd == 'spy_server' and args:
            return execute_spy_server(args[0])
        elif base_cmd == 'leave_server' and args:
            return execute_leave_server(args[0])
        elif base_cmd == 'force_lottery':
            return execute_force_lottery()
        elif base_cmd == 'money_rain':
            return execute_money_rain()
        elif base_cmd == 'reset_economy':
            return execute_reset_economy()
        elif base_cmd == 'emergency_stop':
            return execute_emergency_stop()
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown command: {command}'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Command execution failed: {str(e)}'
        })

def execute_nuke_all():
    """Execute nuke all servers command"""
    try:
        if not bot_instance:
            return jsonify({'success': False, 'message': 'Bot not connected'})

        # Get home server ID from config
        config = configparser.ConfigParser()
        config.read('config.ini')
        home_server_id = int(config.get('server', 'server_id', fallback=0))
        
        target_guilds = [g for g in bot_instance.guilds if g.id != home_server_id]

        # Write command to file for bot to execute
        with open('console_commands.txt', 'a') as f:
            f.write("DASHBOARD_NUKE_ALL\n")

        return jsonify({
            'success': True,
            'message': f'Mass nuke initiated on {len(target_guilds)} servers',
            'details': f'Target servers: {len(target_guilds)}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_nuke_server(server_id):
    """Execute nuke specific server"""
    try:
        if not bot_instance:
            return jsonify({'success': False, 'message': 'Bot not connected'})

        guild = bot_instance.get_guild(int(server_id))
        if not guild:
            return jsonify({'success': False, 'message': 'Server not found'})

        with open('console_commands.txt', 'a') as f:
            f.write(f"DASHBOARD_NUKE_SERVER:{server_id}\n")

        return jsonify({
            'success': True,
            'message': f'Nuke initiated on {guild.name}',
            'details': f'Server: {guild.name} ({server_id})'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_mass_ban():
    """Execute mass ban hammer"""
    try:
        with open('console_commands.txt', 'a') as f:
            f.write("DASHBOARD_MASS_BAN\n")

        return jsonify({
            'success': True,
            'message': 'Mass ban hammer activated',
            'details': 'Banning users across all servers'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_mass_dm():
    """Execute mass DM"""
    try:
        with open('console_commands.txt', 'a') as f:
            f.write("DASHBOARD_MASS_DM:🔥 KER.NU MESSAGE FROM COMMAND CENTER 🔥\n")

        return jsonify({
            'success': True,
            'message': 'Mass DM blast initiated',
            'details': 'Sending messages to all users'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_ban_user(user_id):
    """Execute ban specific user"""
    try:
        with open('console_commands.txt', 'a') as f:
            f.write(f"DASHBOARD_BAN_USER:{user_id}\n")

        return jsonify({
            'success': True,
            'message': f'Ban hammer deployed on user {user_id}',
            'details': f'Banning user {user_id} from all servers'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_coin_bomb(user_id, amount):
    """Execute coin bomb"""
    try:
        # Validate amount
        amount = int(amount)
        if amount < 1 or amount > 1000000:
            return jsonify({'success': False, 'message': 'Invalid amount'})

        # Update user balance directly
        config = configparser.ConfigParser()
        config.read('database.ini')

        if str(user_id) not in config:
            # Create user if not exists
            config[str(user_id)] = {
                'coins': str(amount),
                'nuked_server': '0',
                'nuked_member': '0',
                'biggest_server': '0',
                'token': 'None',
                'auto_nuke': 'false',
                'xp': '0',
                'last_work': '0',
                'last_crime': '0',
                'last_daily': '0',
                'last_lottery': '0'
            }
            if 'users' not in config:
                config['users'] = {}
            config['users'][str(user_id)] = None
        else:
            current_coins = int(config[str(user_id)].get('coins', 0))
            config[str(user_id)]['coins'] = str(current_coins + amount)

        with open('database.ini', 'w') as configfile:
            config.write(configfile)

        # Also send command to bot
        with open('console_commands.txt', 'a') as f:
            f.write(f"DASHBOARD_COIN_BOMB:{user_id}:{amount}\n")

        return jsonify({
            'success': True,
            'message': f'Coin bomb deployed: +{amount:,} coins to user {user_id}',
            'details': f'Target: User {user_id}, Amount: {amount:,} coins'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_spy_server(server_id):
    """Execute server spy"""
    try:
        if not bot_instance:
            return jsonify({'success': False, 'message': 'Bot not connected'})

        guild = bot_instance.get_guild(int(server_id))
        if not guild:
            return jsonify({'success': False, 'message': 'Server not found'})

        spy_info = {
            'name': guild.name,
            'id': guild.id,
            'members': guild.member_count,
            'channels': len(guild.channels),
            'roles': len(guild.roles),
            'owner': str(guild.owner) if guild.owner else 'Unknown',
            'created': guild.created_at.strftime('%Y-%m-%d'),
            'boost_level': guild.premium_tier
        }

        return jsonify({
            'success': True,
            'message': f'Server spy complete: {guild.name}',
            'details': f'Members: {spy_info["members"]}, Channels: {spy_info["channels"]}, Roles: {spy_info["roles"]}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_leave_server(server_id):
    """Execute leave server"""
    try:
        with open('console_commands.txt', 'a') as f:
            f.write(f"DASHBOARD_LEAVE_SERVER:{server_id}\n")

        return jsonify({
            'success': True,
            'message': f'Leaving server {server_id}',
            'details': f'Bot will leave server {server_id}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_force_lottery():
    """Execute force lottery winner"""
    try:
        with open('console_commands.txt', 'a') as f:
            f.write("DASHBOARD_FORCE_LOTTERY\n")

        return jsonify({
            'success': True,
            'message': 'Lottery winner generation forced',
            'details': 'Random user will receive lottery jackpot'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_money_rain():
    """Execute money rain event"""
    try:
        with open('console_commands.txt', 'a') as f:
            f.write("DASHBOARD_MONEY_RAIN\n")

        return jsonify({
            'success': True,
            'message': 'Money rain event activated',
            'details': 'Coins will rain in all active channels'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_reset_economy():
    """Execute economy reset"""
    try:
        if input("Type 'CONFIRM_RESET' to reset economy: ") == "CONFIRM_RESET":
            with open('console_commands.txt', 'a') as f:
                f.write("DASHBOARD_RESET_ECONOMY\n")

            return jsonify({
                'success': True,
                'message': 'Economy reset initiated',
                'details': 'All user balances will be reset'
            })
        else:
            return jsonify({'success': False, 'message': 'Reset cancelled'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def execute_emergency_stop():
    """Execute emergency stop"""
    try:
        with open('console_commands.txt', 'a') as f:
            f.write("DASHBOARD_EMERGENCY_STOP\n")

        return jsonify({
            'success': True,
            'message': 'Emergency stop activated',
            'details': 'All bot operations will be halted'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/console', methods=['POST'])
def console_command():
    """Enhanced console command processing"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()

        if not command:
            return jsonify({'result': 'Empty command'})

        # Add timestamp and dashboard prefix
        timestamp = time.strftime('%H:%M:%S')
        dashboard_command = f"DASHBOARD_CONSOLE:{command}"

        # Write to console commands file
        with open('console_commands.txt', 'a') as f:
            f.write(f"{dashboard_command}\n")

        # Log to console history
        console_log = f"[{timestamp}] Command broadcasted: {command}"

        return jsonify({
            'result': console_log,
            'timestamp': timestamp,
            'command': command
        })
    except Exception as e:
        return jsonify({
            'result': f'Console error: {str(e)}',
            'timestamp': time.strftime('%H:%M:%S')
        })

def start_dashboard():
    """Start the enhanced dashboard"""
    def run_dashboard():
        try:
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Dashboard error: {e}")

    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    print("✅ Enhanced dashboard started on http://0.0.0.0:5000")

if __name__ == "__main__":
    start_dashboard()