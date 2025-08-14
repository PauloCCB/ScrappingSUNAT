from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def main():
    """
    Realiza web scraping en la página de la SUNAT para obtener datos de un RUC.
    """
    # URL de la consulta RUC de SUNAT
    url="https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
    driver=None;
    try:
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        print("Accediendo a la página de la SUNAT...")
        driver.get(url)

        # Esperar a que la página se cargue completamente
        # Esperar a que el campo de RUC esté disponible y escribir el número
        ruc_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "txtRuc"))
        )


        ruc_input.send_keys("20601460913")

                # Hacer clic en el botón de buscar
        btn_consultar = driver.find_element(By.ID, "btnAceptar")
        btn_consultar.click()

        print("Extrayendo información...")

        # Esperar a que la tabla de resultados principal aparezca
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-group"))
        )

        # Obtener el contenido de la página
        #html_content = driver.page_source

        #print("Pagina cargada correctamente")

        # Guardar el contenido en un archivo HTML
        #with open("inside.html", "w", encoding="utf-8") as file:
        #    file.write(html_content)

        ##print("Contenido guardado en inside.html")
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

        #Extraer del tbody de la tabla de cantidad , el ulitmo  dato de numero de trabajadores y numero de prestadores de servicio
        xpath_cantidad_trabajadores="//tbody/tr/td[2]"
        elemento_td_cantidad_trabajadores = driver.find_element(By.XPATH, xpath_cantidad_trabajadores)
        texto_completo_cantidad_trabajadores = elemento_td_cantidad_trabajadores.text
        cantidad_trabajadores=texto_completo_cantidad_trabajadores.strip()

        xpath_cantidad_prestadores_servicio="//tbody/tr/td[4]"
        elemento_td_cantidad_prestadores_servicio = driver.find_element(By.XPATH, xpath_cantidad_prestadores_servicio)
        texto_completo_cantidad_prestadores_servicio = elemento_td_cantidad_prestadores_servicio.text
        cantidad_prestadores_servicio=texto_completo_cantidad_prestadores_servicio.strip()

        print(f"La Razón Social es: {razon_social}") 
        print(f"El Nombre Comercial es: {texto_completo_nombre_comercial}") 
        print(f"El Distrito es: {distrito}") 
        print(f"El Provincia es: {provincia}") 
        print(f"El Departamento es: {departamento}") 
        print(f"La Dirección es: {direccion}") 
        print(f"El Rubro es: {rubro}") 
        print(f"Es agente de retencion : {padrones}") 
        print(f"La cantidad de trabajadores es: {cantidad_trabajadores}") 
        print(f"La cantidad de prestadores de servicio es: {cantidad_prestadores_servicio}") 
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()