#!/usr/bin/env node

// Test script to verify y-websocket server room-based connections
const WebSocket = require('ws');

console.log('🧪 Testing y-websocket server room-based connections...');

// Test 1: Basic connection to IPv4
console.log('\n1️⃣ Testing basic WebSocket connection (IPv4)...');
const basicWs = new WebSocket('ws://127.0.0.1:1234');

basicWs.on('open', () => {
    console.log('✅ Basic connection successful (IPv4)');
    basicWs.close();
});

basicWs.on('error', (error) => {
    console.log('❌ Basic connection failed (IPv4):', error.message);
});

// Test 2: Basic connection to IPv6
setTimeout(() => {
    console.log('\n2️⃣ Testing basic WebSocket connection (IPv6)...');
    const basicWs6 = new WebSocket('ws://[::1]:1234');

    basicWs6.on('open', () => {
        console.log('✅ Basic connection successful (IPv6)');
        basicWs6.close();
    });

    basicWs6.on('error', (error) => {
        console.log('❌ Basic connection failed (IPv6):', error.message);
    });
}, 1000);

// Test 3: Room-based connection
setTimeout(() => {
    console.log('\n3️⃣ Testing room-based connection...');
    const roomWs = new WebSocket('ws://127.0.0.1:1234/test-room-123');

    roomWs.on('open', () => {
        console.log('✅ Room-based connection successful');
        roomWs.close();
    });

    roomWs.on('error', (error) => {
        console.log('❌ Room-based connection failed:', error.message);
    });

    roomWs.on('close', () => {
        console.log('🔌 Room-based connection closed');
    });
}, 2000);

// Test 4: Your specific room
setTimeout(() => {
    console.log('\n4️⃣ Testing your specific room...');
    const specificRoom = 'file-collaboration-8aee99ec-c500-4329-bafd-1c9f28da1045';
    const specificWs = new WebSocket(`ws://127.0.0.1:1234/${specificRoom}`);

    specificWs.on('open', () => {
        console.log('✅ Specific room connection successful');
        specificWs.close();
    });

    specificWs.on('error', (error) => {
        console.log('❌ Specific room connection failed:', error.message);
    });

    specificWs.on('close', () => {
        console.log('🔌 Specific room connection closed');
    });
}, 3000);

// Cleanup after tests
setTimeout(() => {
    console.log('\n🏁 Tests completed');
    process.exit(0);
}, 5000);
