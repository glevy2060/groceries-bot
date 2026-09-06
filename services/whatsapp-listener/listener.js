import { Client, LocalAuth, MessageMedia } from 'whatsapp-web.js';
import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';
const TARGET_GROUP_NAME = process.env.TARGET_GROUP_NAME || 'קניות';
const SESSION_DIR = process.env.SESSION_DIR || path.join(__dirname, '.wppconnect');

const client = new Client({
  authStrategy: new LocalAuth({ clientId: 'groceries-bot', dataPath: SESSION_DIR }),
  puppeteer: {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
});

client.on('qr', (qr) => {
  console.log('📱 Scan this QR code with WhatsApp to authenticate:');
  console.log(qr);
});

client.on('authenticated', () => {
  console.log('✅ WhatsApp authenticated! Listening for messages in "' + TARGET_GROUP_NAME + '"...');
});

client.on('ready', () => {
  console.log('🚀 WhatsApp client is ready');
});

client.on('message', async (message) => {
  try {
    const chat = await message.getChat();

    if (!chat.isGroup) {
      console.log(`⏭️  Skipping private message from ${message.from}`);
      return;
    }

    if (chat.name !== TARGET_GROUP_NAME) {
      console.log(`⏭️  Skipping message from group "${chat.name}" (looking for "${TARGET_GROUP_NAME}")`);
      return;
    }

    const sender = await message.getContact();
    const senderName = sender.pushname || sender.name || message.from;

    console.log(`💬 [${chat.name}] ${senderName}: ${message.body}`);

    try {
      const response = await axios.post(`${PYTHON_API_URL}/whatsapp/message`, {
        text: message.body,
        sender: senderName,
        sender_id: message.from,
        group_name: chat.name,
        group_id: chat.id._serialized,
      }, { timeout: 30000 });

      const reply = response.data.reply;
      if (reply) {
        await chat.sendMessage(reply);
        console.log(`📤 Sent reply to ${chat.name}`);
      }
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        console.error(`❌ Could not reach Python API at ${PYTHON_API_URL}. Is the server running?`);
      } else {
        console.error(`❌ Error calling Python API:`, error.message);
      }
      await chat.sendMessage('❌ Sorry, I encountered an error. Please try again.');
    }
  } catch (error) {
    console.error('❌ Error processing message:', error);
  }
});

client.on('disconnected', (reason) => {
  console.log('⚠️  WhatsApp disconnected:', reason);
  process.exit(1);
});

client.initialize();
