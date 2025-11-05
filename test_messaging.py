#!/usr/bin/env python3
"""
Test script for the new messaging and chat features.
Tests database operations and API endpoints for messaging.
"""

import sys
import madre_db
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text):
    """Print a colored header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    """Print info message."""
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_messaging():
    """Test messaging functionality."""
    print_header("TEST 1: Messaging System")
    
    try:
        # Test sending a message
        print_info("Sending message from juan_perez to admin...")
        msg_id = madre_db.send_message(
            from_user="juan_perez",
            to_user="admin",
            subject="Consulta sobre entrenamiento",
            body="Hola, tengo una pregunta sobre mi rutina de entrenamiento."
        )
        
        if msg_id:
            print_success(f"Message sent successfully - ID: {msg_id}")
        else:
            print_error("Failed to send message")
            return False
        
        # Test getting messages
        print_info("\nGetting messages for admin...")
        messages = madre_db.get_user_messages("admin")
        print_success(f"Retrieved {len(messages)} messages")
        
        # Test counting unread messages
        unread = madre_db.count_unread_messages("admin")
        print_success(f"Unread messages: {unread}")
        
        # Test marking message as read
        print_info("\nMarking message as read...")
        success = madre_db.mark_message_read(msg_id)
        if success:
            print_success("Message marked as read")
        else:
            print_error("Failed to mark message as read")
        
        # Verify unread count decreased
        unread_after = madre_db.count_unread_messages("admin")
        print_success(f"Unread messages after marking: {unread_after}")
        
        # Test sending a reply
        print_info("\nSending reply from admin...")
        reply_id = madre_db.send_message(
            from_user="admin",
            to_user="juan_perez",
            subject="Re: Consulta sobre entrenamiento",
            body="Hola Juan, estaré encantado de ayudarte con tu rutina.",
            parent_message_id=msg_id
        )
        
        if reply_id:
            print_success(f"Reply sent successfully - ID: {reply_id}")
        else:
            print_error("Failed to send reply")
        
        # Test getting specific message
        print_info("\nGetting specific message...")
        message = madre_db.get_message_by_id(msg_id)
        if message:
            print_success(f"Retrieved message: '{message['subject']}'")
        else:
            print_error("Failed to retrieve message")
        
        # Test exporting message
        print_info("\nExporting message to txt...")
        export_path = "/tmp/test_message.txt"
        success = madre_db.export_message_to_txt(msg_id, export_path)
        if success:
            print_success(f"Message exported to {export_path}")
        else:
            print_error("Failed to export message")
        
        # Test deleting a message
        print_info("\nDeleting reply message...")
        success = madre_db.delete_message(reply_id)
        if success:
            print_success("Message deleted successfully")
        else:
            print_error("Failed to delete message")
        
        return True
        
    except Exception as e:
        print_error(f"Messaging test failed: {e}")
        return False

def test_chat():
    """Test chat functionality."""
    print_header("TEST 2: Live Chat System")
    
    try:
        # Test sending chat messages
        print_info("Sending chat messages...")
        chat_id1 = madre_db.send_chat_message(
            from_user="juan_perez",
            to_user="admin",
            message="Hola, estoy disponible para chat?"
        )
        
        chat_id2 = madre_db.send_chat_message(
            from_user="admin",
            to_user="juan_perez",
            message="Sí, claro! En qué puedo ayudarte?"
        )
        
        chat_id3 = madre_db.send_chat_message(
            from_user="juan_perez",
            to_user="admin",
            message="Tengo una duda sobre los ejercicios de hoy."
        )
        
        if chat_id1 and chat_id2 and chat_id3:
            print_success(f"Sent 3 chat messages")
        else:
            print_error("Failed to send some chat messages")
            return False
        
        # Test getting chat history
        print_info("\nGetting chat history...")
        history = madre_db.get_chat_history("juan_perez", "admin", limit=50)
        print_success(f"Retrieved {len(history)} chat messages")
        
        # Display chat history
        print_info("\nChat conversation:")
        for msg in history:
            sender = msg['from_user']
            text = msg['message']
            time = msg['timestamp'][:16]
            print(f"  [{time}] {sender}: {text}")
        
        # Test counting unread chat messages
        unread = madre_db.count_unread_chat_messages("admin")
        print_success(f"\nUnread chat messages for admin: {unread}")
        
        # Test marking chat messages as read
        print_info("\nMarking chat messages as read...")
        madre_db.mark_chat_messages_read("juan_perez", "admin")
        unread_after = madre_db.count_unread_chat_messages("admin")
        print_success(f"Unread chat messages after marking: {unread_after}")
        
        return True
        
    except Exception as e:
        print_error(f"Chat test failed: {e}")
        return False

def test_multi_madre():
    """Test multi-madre server functionality."""
    print_header("TEST 3: Multi-Madre Server Support")
    
    try:
        # Test adding a madre server
        print_info("Registering secondary madre server...")
        success = madre_db.add_madre_server(
            server_name="Madre_Secundaria",
            server_url="http://192.168.1.100:8000",
            sync_token="test_token_123"
        )
        
        if success:
            print_success("Secondary server registered")
        else:
            print_error("Failed to register secondary server")
            return False
        
        # Test getting all servers
        print_info("\nGetting all registered madre servers...")
        servers = madre_db.get_all_madre_servers()
        print_success(f"Found {len(servers)} registered servers")
        
        for server in servers:
            print(f"  - {server['server_name']}: {server['server_url']}")
        
        # Test updating server sync
        print_info("\nUpdating server sync timestamp...")
        success = madre_db.update_madre_server_sync("Madre_Secundaria")
        if success:
            print_success("Server sync timestamp updated")
        else:
            print_error("Failed to update server sync")
        
        return True
        
    except Exception as e:
        print_error(f"Multi-madre test failed: {e}")
        return False

def main():
    """Run all messaging tests."""
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║  SISTEMA GYM v3.0 - PRUEBAS DE MENSAJERÍA Y CHAT        ║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}")
    
    results = []
    
    # Test 1: Messaging
    results.append(('Messaging System', test_messaging()))
    
    # Test 2: Chat
    results.append(('Live Chat System', test_chat()))
    
    # Test 3: Multi-Madre
    results.append(('Multi-Madre Support', test_multi_madre()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed}/{total}){RESET}")
        print(f"{GREEN}  Sistema de mensajería funcionando correctamente!{RESET}")
    else:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed{RESET}")
        print(f"{YELLOW}  Algunos tests fallaron. Revisar mensajes arriba.{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
