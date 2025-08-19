from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

def main(ruc_numero):
    """
    Realiza web scraping en la página de la SUNAT para obtener datos de un RUC.
    
    Args:
        ruc_numero (str): Número de RUC a consultar
        
    Returns:
        dict: Diccionario con toda la información del RUC
    """
    # URL de la consulta RUC de SUNAT
    url="https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
    driver=None;
    try:

    # --- INICIO DE LA MODIFICACIÓN ---
        options = ChromeOptions()
        
        # Añade un User-Agent para simular un navegador real
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        options.add_argument(f'user-agent={user_agent}')
        
        # Opciones para evitar la detección de automatización
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Iniciar el navegador maximizado
        options.add_argument("--start-maximized")
        # --- FIN DE LA MODIFICACIÓN ---


        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        print("Accediendo a la página de la SUNAT...")
        driver.get(url)

        # Esperar a que el campo de RUC esté disponible y escribir el número
        ruc_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "txtRuc"))
        )


        ruc_input.send_keys(ruc_numero)

                # Hacer clic en el botón de buscar
        btn_consultar = driver.find_element(By.ID, "btnAceptar")
        btn_consultar.click()

        print("Extrayendo información...")

        # Esperar a que la tabla de resultados principal aparezca
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-group"))
        )


        datos_ruc={}
        # Extraer Razón Social
        # La información está dentro de varios divs, usamos XPath para una búsqueda más precisa.
        ##Explicacion del codigo:

        #' // h4[contains(text(), 'Número de RUC:')]: Busca cualquier <h4> en el documento que contenga el texto "Número de RUC:".

        #/parent::div: Sube al elemento padre, que es <div class="col-sm-5">.

        #/following-sibling::div: Busca el siguiente "hermano" div, que es <div class="col-sm-7">.

        #/h4: Selecciona la etiqueta <h4> dentro de ese div, que es la que contiene el texto que buscas.
        xpath_razon_social = "//h4[contains(text(), 'Número de RUC:')]/parent::div/following-sibling::div/h4"


        # Obtener el elemento
        elemento_h4 = driver.find_element(By.XPATH,  xpath_razon_social)
    
        # Extraer el texto completo: "20601460913 - CORPELIMA S.A.C."
        texto_completo_razon_social = elemento_h4.text
    
        # Dividir el texto por el guion y obtener la segunda parte
        razon_social = texto_completo_razon_social.split(' - ')[1].strip()

        xpath_nombre_comercial = "//h4[contains(text(), 'Nombre Comercial:')]/parent::div/following-sibling::div/p"
        elemento_p_nombre_comercial = driver.find_element(By.XPATH, xpath_nombre_comercial)
        texto_completo_nombre_comercial = elemento_p_nombre_comercial.text

        xpath_fecha_inicio_actividades = "//h4[contains(text(), 'Fecha de Inicio de Actividades:')]/parent::div/following-sibling::div/p"
        elemento_p_fecha_inicio_actividades = driver.find_element(By.XPATH, xpath_fecha_inicio_actividades)
        texto_completo_fecha_inicio_actividades = elemento_p_fecha_inicio_actividades.text
        fecha_inicio_actividades = texto_completo_fecha_inicio_actividades.strip()

        xpath_tipo_contribuyente = "//h4[contains(text(), 'Tipo Contribuyente:')]/parent::div/following-sibling::div/p"
        elemento_p_tipo_contribuyente = driver.find_element(By.XPATH, xpath_tipo_contribuyente)
        texto_completo_tipo_contribuyente = elemento_p_tipo_contribuyente.text
        tipo_contribuyente = texto_completo_tipo_contribuyente.strip()


        ##Lógica de domicilio fiscal
        #Si el texto completo del domicilio fiscal es "-", entonces se asignan valores por defecto.
        direccion = "No especificado"
        departamento = "No especificado"
        provincia = "No especificado"
        distrito = "No especificado"

        #Si el texto completo del domicilio fiscal no es "-", entonces se divide la cadena por el guion "-" y se asignan los valores correspondientes.
        xpath_domicilio_fiscal="//h4[contains(text(), 'Domicilio Fiscal:')]/parent::div/following-sibling::div/p"
        elemento_p_domicilio_fiscal = driver.find_element(By.XPATH, xpath_domicilio_fiscal)
        texto_completo_domicilio_fiscal = elemento_p_domicilio_fiscal.text
        print(texto_completo_domicilio_fiscal)
        partes = texto_completo_domicilio_fiscal.rsplit("-", 2)
        if len(partes) == 3:
           distrito = partes[2].strip()
           provincia = partes[1].strip()
           direccion_y_depto = partes[0].strip()

           partes_direccion = direccion_y_depto.rsplit(" ", 1)
           if len(partes_direccion) == 2:
              departamento = partes_direccion[1].strip()
              direccion = partes_direccion[0].strip()
           else:
              direccion = direccion_y_depto
        else:
            direccion = texto_completo_domicilio_fiscal.strip()

        #Rubro
        xpath_rubro="//h4[contains(text(), 'Actividad(es) Económica(s):')]/parent::div/following-sibling::div/table/tbody/tr/td"
        elemento_td_rubro = driver.find_element(By.XPATH, xpath_rubro)
        texto_completo_rubro = elemento_td_rubro.text
        rubro=""
      
        partes_rubro=texto_completo_rubro.rsplit(" - ")
        if len(partes_rubro) > 1:
            rubro=partes_rubro[-1].strip()
        else:
            rubro="-"

        #Padrones
        xpath_padrones="//h4[contains(text(), 'Padrones:')]/parent::div/following-sibling::div/table/tbody/tr/td"
        elemento_td_padrones = driver.find_element(By.XPATH, xpath_padrones)
        texto_completo_padrones = elemento_td_padrones.text
        padrones=False
        if texto_completo_padrones != "NINGUNO":
            padrones=True
        else:
            padrones=False

        # Hacer clic en el botón de Cantidad de Trabajadores y/o Prestadores de Servicio
        btn_consultar = driver.find_element(By.CLASS_NAME, "btnInfNumTra")
        btn_consultar.click()

        print("Extrayendo información...")
                # Esperar a que la tabla de resultados principal aparezca
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "formEnviar"))
        )

        ##Traer en archivo .html  el contenido de la pagina
        ##cantidad_content = driver.page_source
        #with open("cantidad.html", "w", encoding="utf-8") as file:
        #    file.write(cantidad_content)
        
        #print("Contenido guardado en cantidad.html")

        # Extraer del tbody de la tabla de cantidad el último dato de número de trabajadores y número de prestadores de servicio
        cantidad_trabajadores = "Sin datos"
        cantidad_prestadores_servicio = "Sin datos"
        
        try:
            # Primero verificar si existe al menos una fila en la tabla
            xpath_verificar_filas = "//table[@class='table']//tbody/tr"
            filas = driver.find_elements(By.XPATH, xpath_verificar_filas)
            
            if len(filas) > 0:
                print(f"Se encontraron {len(filas)} filas en la tabla")
                # Si hay filas, obtener la última
                xpath_cantidad_trabajadores = "//table[@class='table']//tbody/tr[last()]/td[2]"
                elemento_td_cantidad_trabajadores = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_cantidad_trabajadores))
                )
                cantidad_trabajadores = elemento_td_cantidad_trabajadores.text.strip()
                
                xpath_cantidad_prestadores_servicio = "//table[@class='table']//tbody/tr[last()]/td[4]"
                elemento_td_cantidad_prestadores_servicio = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_cantidad_prestadores_servicio))
                )
                cantidad_prestadores_servicio = elemento_td_cantidad_prestadores_servicio.text.strip()
            else:
                print("No se encontraron filas en la tabla de cantidad de trabajadores")
                
        except Exception as e:
            print(f"Error al extraer datos de cantidad: {e}")
            cantidad_trabajadores = "Sin datos"
            cantidad_prestadores_servicio = "Sin datos"

        #Esperar 5 segundos
        time.sleep(2)
        btn_volver = driver.find_element(By.CLASS_NAME, "btnNuevaConsulta")
        btn_volver.click()
        time.sleep(2)

        btn_representates_legales = driver.find_element(By.CLASS_NAME, "btnInfRepLeg")
        btn_representates_legales.click()
        time.sleep(2)

        #with open("representantes_legales.html", "w", encoding="utf-8") as file:
        #    file.write(driver.page_source)

        # Inicializar variables del representante legal
        documento_representante = "Sin datos"
        nro_documento_representante = "Sin datos"
        nombre_representante = "Sin datos"
        cargo_representante = "Sin datos"
        fecha_representante = "Sin datos"
        
        try:
            # Buscar específicamente la fila que contiene "GERENTE GENERAL"
            xpath_fila_gerente = "//table[@class='table']//tbody/tr[td[contains(text(), 'GERENTE')]]"
            fila_gerente = driver.find_element(By.XPATH, xpath_fila_gerente)
            
            # Obtener cada campo de la fila del gerente general
            documento_representante = fila_gerente.find_element(By.XPATH, "./td[1]").text.strip()
            nro_documento_representante = fila_gerente.find_element(By.XPATH, "./td[2]").text.strip()
            nombre_representante = fila_gerente.find_element(By.XPATH, "./td[3]").text.strip()
            cargo_representante = fila_gerente.find_element(By.XPATH, "./td[4]").text.strip()
            fecha_representante = fila_gerente.find_element(By.XPATH, "./td[5]").text.strip()
            
            print("Se encontró información del Gerente General")
            
        except Exception as e:
            print(f"Error al extraer datos del Gerente General: {e}")
            # Si no se encuentra GERENTE GENERAL, intentar obtener el primer representante
            try:
                xpath_primera_fila = "//table[@class='table']//tbody/tr[1]"
                primera_fila = driver.find_element(By.XPATH, xpath_primera_fila)
                
                documento_representante = primera_fila.find_element(By.XPATH, "./td[1]").text.strip()
                nro_documento_representante = primera_fila.find_element(By.XPATH, "./td[2]").text.strip()
                nombre_representante = primera_fila.find_element(By.XPATH, "./td[3]").text.strip()
                cargo_representante = primera_fila.find_element(By.XPATH, "./td[4]").text.strip()
                fecha_representante = primera_fila.find_element(By.XPATH, "./td[5]").text.strip()
                
                print("Se obtuvo información del primer representante legal")
                
            except Exception as e2:
                print(f"Error al extraer datos de representantes legales: {e2}")

        # Crear el diccionario de respuesta
        resultado = {
            "numeroDocumento": ruc_numero,
            "razonSocial": razon_social,
            "nombreComercial": texto_completo_nombre_comercial if texto_completo_nombre_comercial != "-" else "-",
            "direccion": direccion,
            "distrito": distrito,
            "provincia": provincia,
            "departamento": departamento,
            "fechaInicioActividades": fecha_inicio_actividades,
            "EsAgenteRetencion": padrones,
            "actividadEconomica": rubro,
            "tipoContribuyente": tipo_contribuyente,
            "numeroTrabajadores": cantidad_trabajadores,
            "prestadoresdeServicios": cantidad_prestadores_servicio,
            "representanteLegal": {
                "tipoDocumento": documento_representante,
                "nroDocumento": nro_documento_representante,
                "nombre": nombre_representante,
                "cargo": cargo_representante,
                "fechaDesde": fecha_representante
            }
        }
        
        print("Información extraída exitosamente:")
        print(f"RUC: {resultado['numeroDocumento']}")
        print(f"Razón Social: {resultado['razonSocial']}")
        print(f"Representante Legal: {resultado['representanteLegal']['nombre']}")
        
        return resultado 
    except Exception as e:
        print(f"Error: {e}")
        return {
            "numeroDocumento": ruc_numero,
            "razonSocial": "Error en consulta",
            "nombreComercial": "Sin datos",
            "direccion": "Sin datos",
            "distrito": "Sin datos",
            "provincia": "Sin datos",
            "departamento": "Sin datos",
            "fechaInicioActividades": "Sin datos",
            "EsAgenteRetencion": False,
            "actividadEconomica": "Sin datos",
            "tipoContribuyente": "Sin datos",
            "numeroTrabajadores": "Sin datos",
            "prestadoresdeServicios": "Sin datos",
            "representanteLegal": {
                "tipoDocumento": "Sin datos",
                "nroDocumento": "Sin datos",
                "nombre": "Sin datos",
                "cargo": "Sin datos",
                "fechaDesde": "Sin datos"
            }
        }
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Ejemplo de uso
    ruc_consulta = "20525955096"
    resultado = main(ruc_consulta)
    
    if resultado:
        import json
        print("\n=== RESULTADO EN FORMATO JSON ===")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))