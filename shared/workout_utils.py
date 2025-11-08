# shared/workout_utils.py
#
# Utilidades para entrenamiento: calculadora de discos, temporizadores, etc.

from typing import List, Dict, Tuple


def calculate_plates(target_weight: float, bar_weight: float = 20.0,
                    available_plates: List[float] = None) -> Dict[str, any]:
    """
    Calculadora de discos para barras.
    
    Args:
        target_weight: Peso objetivo total en kg
        bar_weight: Peso de la barra en kg (default 20kg - barra olímpica estándar)
        available_plates: Lista de discos disponibles en kg
        
    Returns:
        Dict con la configuración de discos necesarios
    """
    if available_plates is None:
        # Discos estándar de gimnasio (por lado)
        available_plates = [25.0, 20.0, 15.0, 10.0, 5.0, 2.5, 2.0, 1.25, 1.0, 0.5]
    
    # Calcular peso necesario en discos (ambos lados)
    weight_needed = target_weight - bar_weight
    
    if weight_needed < 0:
        return {
            'success': False,
            'error': f'El peso objetivo ({target_weight}kg) es menor que el peso de la barra ({bar_weight}kg)',
            'target_weight': target_weight,
            'bar_weight': bar_weight
        }
    
    if weight_needed == 0:
        return {
            'success': True,
            'plates_per_side': [],
            'total_plates_weight': 0,
            'total_weight': bar_weight,
            'target_weight': target_weight,
            'bar_weight': bar_weight,
            'message': 'No se necesitan discos, solo la barra'
        }
    
    # Peso necesario por lado
    weight_per_side = weight_needed / 2.0
    
    # Calcular discos necesarios por lado usando algoritmo greedy
    plates_per_side = []
    remaining_weight = weight_per_side
    
    for plate in sorted(available_plates, reverse=True):
        while remaining_weight >= plate - 0.01:  # Tolerancia de 10g por redondeo
            plates_per_side.append(plate)
            remaining_weight -= plate
    
    # Verificar si se alcanzó el peso exacto (con tolerancia)
    actual_weight_per_side = sum(plates_per_side)
    total_weight = bar_weight + (actual_weight_per_side * 2)
    
    if abs(remaining_weight) > 0.1:  # Si quedan más de 100g sin cubrir
        return {
            'success': False,
            'error': f'No se puede alcanzar exactamente {target_weight}kg con los discos disponibles',
            'closest_weight': total_weight,
            'difference': target_weight - total_weight,
            'plates_per_side': plates_per_side,
            'target_weight': target_weight,
            'bar_weight': bar_weight,
            'message': f'Peso más cercano posible: {total_weight}kg (diferencia: {abs(target_weight - total_weight):.1f}kg)'
        }
    
    # Formatear resultado
    plate_counts = {}
    for plate in plates_per_side:
        plate_counts[plate] = plate_counts.get(plate, 0) + 1
    
    return {
        'success': True,
        'plates_per_side': plates_per_side,
        'plate_counts': plate_counts,
        'total_plates_weight': actual_weight_per_side * 2,
        'total_weight': total_weight,
        'target_weight': target_weight,
        'bar_weight': bar_weight,
        'message': 'Configuración de discos calculada correctamente'
    }


def format_plates_result(result: Dict) -> str:
    """
    Formatea el resultado de calculate_plates para mostrar en UI.
    
    Returns:
        String formateado con la configuración de discos
    """
    if not result['success']:
        return f"❌ {result.get('error', 'Error desconocido')}\n{result.get('message', '')}"
    
    lines = []
    lines.append(f"✅ Peso objetivo: {result['target_weight']}kg")
    lines.append(f"📊 Barra: {result['bar_weight']}kg")
    lines.append(f"⚖️  Peso total: {result['total_weight']}kg")
    lines.append("")
    
    if not result['plates_per_side']:
        lines.append("🏋️ No se necesitan discos, solo la barra")
        return "\n".join(lines)
    
    lines.append("🔩 Discos por lado:")
    plate_counts = result.get('plate_counts', {})
    for plate in sorted(plate_counts.keys(), reverse=True):
        count = plate_counts[plate]
        lines.append(f"   • {plate}kg × {count}")
    
    lines.append("")
    lines.append(f"📝 Orden de colocación (por lado):")
    for i, plate in enumerate(result['plates_per_side'], 1):
        lines.append(f"   {i}. {plate}kg")
    
    return "\n".join(lines)


def get_standard_bar_weights() -> List[Tuple[str, float]]:
    """
    Retorna lista de pesos estándar de barras.
    
    Returns:
        Lista de tuplas (nombre, peso_kg)
    """
    return [
        ("Barra Olímpica Estándar", 20.0),
        ("Barra Olímpica Mujer", 15.0),
        ("Barra EZ", 10.0),
        ("Barra Hexagonal (Trap Bar)", 25.0),
        ("Barra Técnica", 5.0),
        ("Barra de Entrenamiento Juvenil", 10.0)
    ]


def calculate_rest_time(exercise_type: str = "strength", intensity: str = "medium") -> int:
    """
    Calcula tiempo de descanso recomendado según tipo de ejercicio e intensidad.
    
    Args:
        exercise_type: Tipo de ejercicio ("strength", "hypertrophy", "endurance", "power")
        intensity: Intensidad ("low", "medium", "high")
        
    Returns:
        Tiempo de descanso recomendado en segundos
    """
    rest_times = {
        "power": {"low": 180, "medium": 240, "high": 300},  # 3-5 min
        "strength": {"low": 120, "medium": 180, "high": 240},  # 2-4 min
        "hypertrophy": {"low": 60, "medium": 90, "high": 120},  # 1-2 min
        "endurance": {"low": 30, "medium": 45, "high": 60}  # 0.5-1 min
    }
    
    return rest_times.get(exercise_type, rest_times["strength"]).get(intensity, 90)


def format_time(seconds: int) -> str:
    """
    Formatea segundos a formato legible.
    
    Returns:
        String formateado (ej: "2:30" o "45s")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if remaining_seconds == 0:
        return f"{minutes}min"
    
    return f"{minutes}:{remaining_seconds:02d}"


# Ejemplo de uso
if __name__ == "__main__":
    # Test calculadora de discos
    print("=== Calculadora de Discos ===\n")
    
    test_weights = [60, 100, 142.5, 200]
    
    for weight in test_weights:
        result = calculate_plates(weight)
        print(format_plates_result(result))
        print("-" * 50)
        print()
