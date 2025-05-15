import os
import pytest

def run_tests():
    # Crear el directorio de informes si no existe
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # Ejecutar las pruebas y generar el informe HTML
    exit_code = pytest.main([
        '--html=reports/report.html',
        '--self-contained-html',
        '-v'
    ])
    
    print(f"\nPruebas completadas. Código de salida: {exit_code}")
    print(f"Puedes encontrar el informe en: {os.path.abspath('reports/report.html')}")

if __name__ == "__main__":
    run_tests()
