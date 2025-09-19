#!/usr/bin/env python3
"""
Análise profunda da estrutura da página
Aguarda carregamento completo e analisa todos os elementos
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

def deep_analysis():
    print("🔬 ANÁLISE PROFUNDA DA PÁGINA")
    print("=" * 60)
    
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://mastercardconnect.com")
        time.sleep(3)
        
        print("\n🎯 Navegue até a página de Announcements...")
        input("Pressione ENTER quando estiver vendo os documentos...")
        
        # Troca para aba mais recente se necessário
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            
        print("\n⏳ Aguardando carregamento completo...")
        time.sleep(10)  # Aguarda mais tempo
        
        # 1. Procura por iframes
        print("\n🖼️ PROCURANDO IFRAMES:")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"   Iframes encontrados: {len(iframes)}")
        
        # 2. Analisa estrutura da tabela/lista
        print("\n📋 ANALISANDO ESTRUTURA DE TABELA/LISTA:")
        
        # Procura por tabelas
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"   Tabelas: {len(tables)}")
        
        for i, table in enumerate(tables[:3]):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"      Tabela {i+1}: {len(rows)} linhas")
            
            # Analisa primeiras linhas
            for j, row in enumerate(rows[:5]):
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    cell_texts = [cell.text.strip()[:30] for cell in cells]
                    print(f"         Linha {j+1}: {len(cells)} células: {cell_texts}")
                    
                    # Procura elementos clicáveis em cada célula
                    for k, cell in enumerate(cells):
                        clickables = cell.find_elements(By.XPATH, ".//a | .//button | .//*[@onclick]")
                        if clickables:
                            print(f"            Célula {k+1}: {len(clickables)} elementos clicáveis")
        
        # 3. Procura por listas (ul, ol, div com lista)
        print(f"\n📝 ANALISANDO LISTAS:")
        
        lists = driver.find_elements(By.CSS_SELECTOR, "ul, ol, [class*='list'], [class*='grid']")
        print(f"   Listas encontradas: {len(lists)}")
        
        for i, lst in enumerate(lists[:3]):
            items = lst.find_elements(By.CSS_SELECTOR, "li, > div, > a")
            print(f"      Lista {i+1}: {len(items)} itens")
            
        # 4. Análise específica por data
        print(f"\n📅 PROCURANDO POR ELEMENTOS COM DATAS:")
        
        # Busca elementos que contenham datas de junho/julho
        date_keywords = ['Jun', 'Jul', '25', '26', '27', '28', '29', '30', '01']
        
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Jun') or contains(text(), 'Jul')]")
        print(f"   Elementos com Jun/Jul: {len(all_elements)}")
        
        date_elements = []
        for elem in all_elements:
            text = elem.text.strip()
            if any(day in text for day in ['25', '26', '27', '28', '29', '30', '01']) and any(month in text for month in ['Jun', 'Jul']):
                date_elements.append(elem)
                
        print(f"   Elementos com datas relevantes: {len(date_elements)}")
        
        # Para cada elemento com data, analisa o contexto ao redor
        for i, date_elem in enumerate(date_elements[:3]):
            print(f"\n   📅 Elemento com data {i+1}:")
            print(f"      Texto: {date_elem.text.strip()[:100]}")
            print(f"      Tag: {date_elem.tag_name}")
            print(f"      Classes: {date_elem.get_attribute('class') or 'nenhuma'}")
            
            # Sobe na hierarquia procurando por container pai
            current = date_elem
            for level in range(10):
                try:
                    parent = current.find_element(By.XPATH, "./..")
                    
                    # Procura elementos clicáveis no container pai
                    clickables = parent.find_elements(By.XPATH, ".//a | .//button | .//*[@onclick] | .//*[contains(@class, 'click')] | .//*[contains(@class, 'btn')]")
                    
                    if clickables:
                        print(f"         Nível {level}: {len(clickables)} clicáveis no container")
                        
                        for j, clickable in enumerate(clickables[:3]):
                            tag = clickable.tag_name
                            classes = clickable.get_attribute('class') or ''
                            href = clickable.get_attribute('href') or ''
                            onclick = clickable.get_attribute('onclick') or ''
                            title = clickable.get_attribute('title') or ''
                            inner_html = clickable.get_attribute('innerHTML')[:100] if clickable.get_attribute('innerHTML') else ''
                            
                            print(f"            {j+1}. <{tag}> classes: {classes[:40]}")
                            
                            if href:
                                print(f"               href: {href[:50]}")
                            if onclick:
                                print(f"               onclick: {onclick[:50]}")
                            if title:
                                print(f"               title: {title}")
                            if inner_html and len(inner_html) < 100:
                                print(f"               innerHTML: {inner_html}")
                                
                    current = parent
                    
                except:
                    break
                    
        # 5. Teste de hover em elementos suspeitos
        print(f"\n🖱️ TESTANDO HOVER EM ELEMENTOS:")
        
        # Procura por elementos que podem revelar downloads no hover
        hover_candidates = driver.find_elements(By.CSS_SELECTOR, 
            "[class*='row'], [class*='item'], [class*='card'], td, .result, .list-item")
        
        print(f"   Candidatos para hover: {len(hover_candidates)}")
        
        actions = ActionChains(driver)
        
        for i, candidate in enumerate(hover_candidates[:5]):
            try:
                # Verifica se tem texto com data
                if any(month in candidate.text for month in ['Jun', 'Jul']):
                    print(f"      Testando hover no elemento {i+1}...")
                    
                    # Conta elementos clicáveis antes do hover
                    clickables_before = len(candidate.find_elements(By.XPATH, ".//a | .//button | .//*[@onclick]"))
                    
                    # Faz hover
                    actions.move_to_element(candidate).perform()
                    time.sleep(2)
                    
                    # Conta elementos clicáveis depois do hover
                    clickables_after = len(candidate.find_elements(By.XPATH, ".//a | .//button | .//*[@onclick]"))
                    
                    if clickables_after > clickables_before:
                        print(f"         ✅ Hover revelou {clickables_after - clickables_before} novos elementos!")
                        
                        # Analisa os novos elementos
                        new_clickables = candidate.find_elements(By.XPATH, ".//a | .//button | .//*[@onclick]")
                        for clickable in new_clickables[-1:]:  # Último elemento (provavelmente novo)
                            print(f"            Novo elemento: <{clickable.tag_name}> {clickable.get_attribute('class')}")
                            
            except Exception as e:
                continue
                
        # 6. Procura por elementos ocultos
        print(f"\n👻 PROCURANDO ELEMENTOS OCULTOS:")
        
        hidden_elements = driver.execute_script("""
            var hidden = [];
            document.querySelectorAll('*').forEach(function(el) {
                var style = window.getComputedStyle(el);
                if ((style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') 
                    && (el.innerHTML.includes('download') || el.className.includes('download'))) {
                    hidden.push({
                        tag: el.tagName,
                        classes: el.className,
                        innerHTML: el.innerHTML.substring(0, 100)
                    });
                }
            });
            return hidden;
        """)
        
        print(f"   Elementos ocultos com 'download': {len(hidden_elements)}")
        for elem in hidden_elements:
            print(f"      <{elem['tag']}> {elem['classes']}")
            
        # 7. Busca por padrões específicos na página
        print(f"\n🔍 BUSCANDO PADRÕES ESPECÍFICOS:")
        
        # Procura por elementos com data-* attributes
        data_elements = driver.find_elements(By.XPATH, "//*[starts-with(@data-url, 'http') or @data-href or @data-link]")
        print(f"   data-url/href/link: {len(data_elements)}")
        
        # Procura por formulários ocultos
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"   Formulários: {len(forms)}")
        
        for form in forms:
            action = form.get_attribute('action')
            if action and ('download' in action or 'export' in action):
                print(f"      Formulário com action de download: {action}")
                
        print(f"\n✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()

if __name__ == "__main__":
    deep_analysis()
