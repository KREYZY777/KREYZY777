#!/usr/bin/env python3
"""
Programa para generar y gestionar giftcards.
Sistema completo para crear, validar y usar tarjetas de regalo.
"""

import json
import os
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class GiftCard:
    """Clase que representa una tarjeta de regalo."""
    
    def __init__(self, code: str, initial_balance: float, expiration_date: str, 
                 pin: str, cvv: str, active: bool = True):
        """
        Inicializa una nueva giftcard.
        
        Args:
            code: Código único de la tarjeta
            initial_balance: Saldo inicial
            expiration_date: Fecha de expiración en formato YYYY-MM-DD
            pin: PIN de seguridad (4 dígitos)
            cvv: CVV de seguridad (3 dígitos)
            active: Estado de la tarjeta (activa/inactiva)
        """
        self.code = code
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.expiration_date = expiration_date
        self.pin = pin
        self.cvv = cvv
        self.active = active
        self.created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.last_used = None
    
    def to_dict(self) -> Dict:
        """Convierte la giftcard a diccionario para JSON."""
        return {
            'code': self.code,
            'balance': self.balance,
            'initial_balance': self.initial_balance,
            'expiration_date': self.expiration_date,
            'pin': self.pin,
            'cvv': self.cvv,
            'active': self.active,
            'created_date': self.created_date,
            'last_used': self.last_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GiftCard':
        """Crea una giftcard desde un diccionario."""
        card = cls(
            code=data['code'],
            initial_balance=data['initial_balance'],
            expiration_date=data['expiration_date'],
            pin=data['pin'],
            cvv=data['cvv'],
            active=data['active']
        )
        card.balance = data['balance']
        card.created_date = data['created_date']
        card.last_used = data.get('last_used')
        return card
    
    def is_expired(self) -> bool:
        """Verifica si la tarjeta ha expirado."""
        try:
            expiration = datetime.strptime(self.expiration_date, '%Y-%m-%d')
            return datetime.now() > expiration
        except ValueError:
            return True
    
    def is_valid(self) -> bool:
        """Verifica si la tarjeta es válida (activa y no expirada)."""
        return self.active and not self.is_expired()


class GiftCardManager:
    """Gestor para operaciones con giftcards."""
    
    def __init__(self, data_file: str = 'giftcards.json'):
        """
        Inicializa el gestor.
        
        Args:
            data_file: Archivo JSON donde se almacenan las giftcards
        """
        self.data_file = data_file
        self.cards = self._load_cards()
    
    def _load_cards(self) -> Dict[str, GiftCard]:
        """Carga las giftcards desde el archivo JSON."""
        if not os.path.exists(self.data_file):
            return {}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {code: GiftCard.from_dict(card_data) 
                       for code, card_data in data.items()}
        except (json.JSONDecodeError, KeyError, ValueError):
            print(f"Error al cargar {self.data_file}. Iniciando con base de datos vacía.")
            return {}
    
    def _save_cards(self) -> None:
        """Guarda las giftcards en el archivo JSON."""
        try:
            data = {code: card.to_dict() for code, card in self.cards.items()}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar las giftcards: {e}")
    
    def _generate_unique_code(self) -> str:
        """Genera un código único para una nueva giftcard."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            if code not in self.cards:
                return code
    
    def _generate_pin(self) -> str:
        """Genera un PIN de 4 dígitos."""
        return ''.join(random.choices(string.digits, k=4))
    
    def _generate_cvv(self) -> str:
        """Genera un CVV de 3 dígitos."""
        return ''.join(random.choices(string.digits, k=3))
    
    def create_giftcard(self, initial_balance: float, 
                       expiration_days: int = 365) -> GiftCard:
        """
        Crea una nueva giftcard.
        
        Args:
            initial_balance: Saldo inicial de la tarjeta
            expiration_days: Días hasta la expiración (por defecto 365)
        
        Returns:
            Nueva giftcard creada
        """
        if initial_balance <= 0:
            raise ValueError("El saldo inicial debe ser mayor que 0")
        
        code = self._generate_unique_code()
        expiration_date = (datetime.now() + timedelta(days=expiration_days)).strftime('%Y-%m-%d')
        pin = self._generate_pin()
        cvv = self._generate_cvv()
        
        card = GiftCard(
            code=code,
            initial_balance=initial_balance,
            expiration_date=expiration_date,
            pin=pin,
            cvv=cvv
        )
        
        self.cards[code] = card
        self._save_cards()
        
        return card
    
    def get_card(self, code: str) -> Optional[GiftCard]:
        """
        Obtiene una giftcard por su código.
        
        Args:
            code: Código de la giftcard
        
        Returns:
            GiftCard si existe, None si no existe
        """
        return self.cards.get(code)
    
    def validate_card(self, code: str, pin: str, cvv: str) -> Tuple[bool, str]:
        """
        Valida una giftcard con PIN y CVV.
        
        Args:
            code: Código de la giftcard
            pin: PIN de seguridad
            cvv: CVV de seguridad
        
        Returns:
            Tupla (válida, mensaje)
        """
        card = self.get_card(code)
        
        if not card:
            return False, "Tarjeta no encontrada"
        
        if not card.active:
            return False, "Tarjeta inactiva"
        
        if card.is_expired():
            return False, "Tarjeta expirada"
        
        if card.pin != pin:
            return False, "PIN incorrecto"
        
        if card.cvv != cvv:
            return False, "CVV incorrecto"
        
        return True, "Tarjeta válida"
    
    def use_balance(self, code: str, pin: str, cvv: str, amount: float) -> Tuple[bool, str]:
        """
        Usa saldo de una giftcard.
        
        Args:
            code: Código de la giftcard
            pin: PIN de seguridad
            cvv: CVV de seguridad
            amount: Cantidad a usar
        
        Returns:
            Tupla (éxito, mensaje)
        """
        if amount <= 0:
            return False, "La cantidad debe ser mayor que 0"
        
        # Validar la tarjeta
        is_valid, message = self.validate_card(code, pin, cvv)
        if not is_valid:
            return False, message
        
        card = self.cards[code]
        
        if card.balance < amount:
            return False, f"Saldo insuficiente. Saldo disponible: ${card.balance:.2f}"
        
        # Usar el saldo
        card.balance -= amount
        card.last_used = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Si el saldo queda en 0, desactivar la tarjeta
        if card.balance == 0:
            card.active = False
        
        self._save_cards()
        
        return True, f"Transacción exitosa. Saldo restante: ${card.balance:.2f}"
    
    def deactivate_card(self, code: str) -> bool:
        """
        Desactiva una giftcard.
        
        Args:
            code: Código de la giftcard
        
        Returns:
            True si se desactivó exitosamente, False si no existe
        """
        card = self.get_card(code)
        if not card:
            return False
        
        card.active = False
        self._save_cards()
        return True
    
    def get_card_info(self, code: str) -> Optional[Dict]:
        """
        Obtiene información básica de una giftcard (sin PIN/CVV).
        
        Args:
            code: Código de la giftcard
        
        Returns:
            Diccionario con información básica o None si no existe
        """
        card = self.get_card(code)
        if not card:
            return None
        
        return {
            'code': card.code,
            'balance': card.balance,
            'initial_balance': card.initial_balance,
            'expiration_date': card.expiration_date,
            'active': card.active,
            'created_date': card.created_date,
            'last_used': card.last_used,
            'is_expired': card.is_expired()
        }
    
    def list_all_cards(self) -> List[Dict]:
        """
        Lista todas las giftcards (información básica).
        
        Returns:
            Lista de diccionarios con información básica de todas las tarjetas
        """
        return [self.get_card_info(code) for code in self.cards.keys()]


def main():
    """
    Función principal con ejemplos de uso del sistema de giftcards.
    """
    print("=== Sistema de Gestión de Giftcards ===\n")
    
    # Crear instancia del gestor
    manager = GiftCardManager()
    
    # Ejemplo 1: Crear una nueva giftcard
    print("1. Creando nueva giftcard...")
    try:
        card = manager.create_giftcard(initial_balance=100.0, expiration_days=365)
        print(f"✓ Giftcard creada exitosamente:")
        print(f"  - Código: {card.code}")
        print(f"  - Saldo: ${card.balance:.2f}")
        print(f"  - Fecha de expiración: {card.expiration_date}")
        print(f"  - PIN: {card.pin}")
        print(f"  - CVV: {card.cvv}")
        print(f"  - Activa: {card.active}")
    except Exception as e:
        print(f"✗ Error al crear giftcard: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 2: Validar giftcard
    print("2. Validando giftcard...")
    is_valid, message = manager.validate_card(card.code, card.pin, card.cvv)
    print(f"Resultado: {message}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 3: Usar saldo de la giftcard
    print("3. Usando saldo de la giftcard...")
    success, message = manager.use_balance(card.code, card.pin, card.cvv, 25.50)
    print(f"Resultado: {message}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 4: Consultar información de la giftcard
    print("4. Consultando información de la giftcard...")
    info = manager.get_card_info(card.code)
    if info:
        print("Información de la tarjeta:")
        for key, value in info.items():
            print(f"  - {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 5: Intentar usar con PIN incorrecto
    print("5. Intentando usar con PIN incorrecto...")
    success, message = manager.use_balance(card.code, "0000", card.cvv, 10.0)
    print(f"Resultado: {message}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 6: Intentar usar más saldo del disponible
    print("6. Intentando usar más saldo del disponible...")
    success, message = manager.use_balance(card.code, card.pin, card.cvv, 200.0)
    print(f"Resultado: {message}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 7: Crear otra giftcard y usar todo el saldo
    print("7. Creando otra giftcard y usando todo el saldo...")
    card2 = manager.create_giftcard(initial_balance=50.0)
    print(f"Nueva giftcard creada: {card2.code}")
    
    # Usar todo el saldo
    success, message = manager.use_balance(card2.code, card2.pin, card2.cvv, 50.0)
    print(f"Usando todo el saldo: {message}")
    
    # Verificar estado
    info = manager.get_card_info(card2.code)
    print(f"Estado después de usar todo el saldo - Activa: {info['active']}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 8: Listar todas las giftcards
    print("8. Listando todas las giftcards...")
    all_cards = manager.list_all_cards()
    print(f"Total de giftcards: {len(all_cards)}")
    for i, card_info in enumerate(all_cards, 1):
        print(f"  Tarjeta {i}:")
        print(f"    - Código: {card_info['code']}")
        print(f"    - Saldo: ${card_info['balance']:.2f}")
        print(f"    - Activa: {card_info['active']}")
        print(f"    - Expirada: {card_info['is_expired']}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 9: Desactivar una giftcard
    print("9. Desactivando una giftcard...")
    if manager.deactivate_card(card.code):
        print("✓ Giftcard desactivada exitosamente")
        info = manager.get_card_info(card.code)
        print(f"Estado actual - Activa: {info['active']}")
    else:
        print("✗ Error al desactivar giftcard")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 10: Intentar usar giftcard desactivada
    print("10. Intentando usar giftcard desactivada...")
    success, message = manager.use_balance(card.code, card.pin, card.cvv, 10.0)
    print(f"Resultado: {message}")
    
    print("\n=== Fin de ejemplos ===")


if __name__ == "__main__":
    main()