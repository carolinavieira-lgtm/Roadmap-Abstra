#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para exportar dados do Roadmap HTML para CSV e JSON
Extrai array 'projects' do arquivo index.html
"""

import json
import csv
import re
from pathlib import Path

def extract_projects_from_html():
    """Extrai os dados de projetos do arquivo index.html"""
    
    html_file = Path("index.html")
    if not html_file.exists():
        print("❌ Erro: arquivo index.html não encontrado!")
        return None
    
    print(f"📂 Lendo {html_file}...")
    
    # Ler o arquivo HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Método 1: Procurar por "const projects=["
    match = re.search(r'const\s+projects\s*=\s*\[(.*?)\];', html_content, re.DOTALL)
    
    if not match:
        print("❌ Padrão 'const projects=[...]' não encontrado!")
        print("Tentando método alternativo...")
        
        # Método 2: Procurar por qualquer array de objetos com "order", "priority", etc
        match = re.search(r'\[\s*\{\s*"order":', html_content, re.DOTALL)
        if match:
            print("✓ Encontrado array com 'order'")
            start = match.start()
            # Encontrar o fim do array
            bracket_count = 0
            in_string = False
            escape_next = False
            end = start
            
            for i in range(start, len(html_content)):
                char = html_content[i]
                
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = i + 1
                            break
            
            projects_json_str = html_content[start:end]
        else:
            print("❌ Não consegui encontrar os projetos!")
            return None
    else:
        projects_json_str = '[' + match.group(1) + ']'
    
    print(f"📝 Tentando fazer parse do JSON...")
    
    try:
        projects = json.loads(projects_json_str)
        print(f"✅ {len(projects)} projetos encontrados!")
        return projects
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao fazer parse do JSON: {e}")
        print(f"String JSON tem {len(projects_json_str)} caracteres")
        return None

def export_to_csv(projects):
    """Exporta projetos para CSV"""
    
    if not projects:
        print("❌ Nenhum projeto para exportar!")
        return False
    
    csv_file = "roadmap_export.csv"
    
    # Definir headers baseado nas chaves do primeiro projeto
    if projects:
        headers = list(projects[0].keys())
    else:
        headers = ["order", "priority", "status", "title", "objective", "value", "nextSteps"]
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(projects)
        
        print(f"✅ CSV criado: {csv_file} ({len(projects)} linhas)")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar CSV: {e}")
        return False

def export_to_json(projects):
    """Exporta projetos para JSON"""
    
    if not projects:
        print("❌ Nenhum projeto para exportar!")
        return False
    
    json_file = "roadmap_export.json"
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON criado: {json_file} ({len(projects)} projetos)")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar JSON: {e}")
        return False

def print_summary(projects):
    """Imprime resumo dos dados"""
    
    if not projects:
        return
    
    print("\n" + "="*60)
    print("📊 RESUMO DO ROADMAP")
    print("="*60)
    
    total = len(projects)
    print(f"\n📌 Total de projetos: {total}")
    
    # Contar por status
    if projects and 'status' in projects[0]:
        status_count = {}
        for project in projects:
            status = project.get("status", "Desconhecido")
            status_count[status] = status_count.get(status, 0) + 1
        
        print("\n📋 Por Status:")
        for status, count in sorted(status_count.items()):
            print(f"   • {status}: {count}")
    
    # Contar por prioridade
    if projects and 'priority' in projects[0]:
        priority_count = {}
        for project in projects:
            priority = project.get("priority", "Desconhecida")
            priority_count[priority] = priority_count.get(priority, 0) + 1
        
        print("\n⭐ Por Prioridade:")
        for priority, count in sorted(priority_count.items()):
            print(f"   • {priority}: {count}")
    
    # Mostrar primeiro projeto como exemplo
    if projects:
        print("\n📌 Exemplo do primeiro projeto:")
        first = projects[0]
        for key, value in first.items():
            print(f"   • {key}: {value}")
    
    print("\n" + "="*60)

def main():
    print("\n" + "="*60)
    print("🚀 EXPORTADOR DE ROADMAP")
    print("="*60)
    
    # Extrair projetos
    projects = extract_projects_from_html()
    
    if not projects:
        print("\n❌ Não foi possível extrair os projetos!")
        return False
    
    # Exportar para CSV
    export_to_csv(projects)
    
    # Exportar para JSON
    export_to_json(projects)
    
    # Mostrar resumo
    print_summary(projects)
    
    print("\n✨ Exportação concluída com sucesso!\n")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
