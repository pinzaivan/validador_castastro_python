import arcpy
import csv
import re
import os

arcpy.env.XYTolerance = "0.001 Meters"

gdb_name = arcpy.GetParameterAsText(0)

gdb_path = os.path.join(gdb_name)

if not arcpy.Exists(gdb_path):
    arcpy.AddError("La GDB especificada no existe.")
else:
    arcpy.AddMessage("La GDB se cargo correctamente.")

# VARIABLES

terrenoctm12 = r"{0}\URBANO_CTM12\U_TERRENO_CTM12".format(gdb_name)
construccionctm12 = r"{0}\URBANO_CTM12\U_CONSTRUCCION_CTM12".format(gdb_name)
unidadconstruccionctm12 = r"{0}\URBANO_CTM12\U_UNIDAD_CTM12".format(gdb_name)
nomeclaturadom = r"{0}\URBANO_CTM12\U_NOMEN_DOMICILIARIA_CTM12".format(gdb_name)
manzanactm12 = r"{0}\URBANO_CTM12\U_MANZANA_CTM12".format(gdb_name)
intersectctm12 = r"{0}\INTERSECT".format(gdb_name)           


# ARCHIVO DE SALIDA

output_csv = r"C:\temp\resultados_validacion.csv"

# FUNCIONES
def validar_codigo(codigo):
    if codigo is None or codigo.strip() == "":
        return "Invalido: codigo vacio"
    if len(codigo) != 30:
        return "Invalido: Longitud incorrecta"
    if not codigo.isdigit():
        return "Invalido: Contiene caracteres especiales"
    if codigo[0:2] != "41":
        return "Invalido: Error en codigo departamento"
    if codigo[2:5] != "013":
        return "Invalido: Error en codigo municipio"
    if codigo[9:13] != "0000":
        return "Invalido: Error en codigo barrio y comuna"
    if codigo[13:17] == "0000":
        return "Invalido: Manzana sin codigo"
    if codigo[17:21] == "0000":
        return "Invalido: Terreno sin codigo"
    if codigo[21:29] == "000000000":
        return "Invalido: Posiciones 22 a 30 deben ser '00000'"
    if codigo[21] == "9":
        return "Valido: PROPIEDAD HORIZONTAL"
    if codigo[21] == "2":
        return "Invalido: terreno INFORMAL"
    if codigo[21] == "8":
        return "Valido: CONDOMINIO"
    if codigo[21] == "7":
        return "Invalido: PARQUE CEMENTERIO"
    if codigo[21] == "4":
        return "Invalido: VIAS"
    if codigo[21] == "3":
        return "Invalido: BIENES DE USO PUBLICO"
    if codigo[21] == "1":
        return "Invalido: condicion de NPN invalida"
    if codigo[21] == "5":
        return "Invalido: conidicion de NPN invalida"
    if codigo[21] == "6":
        return "Invalido: condicion de NPN invalida"
    
    return "Valido"

def validar_codigo_informal(codigo):
    if codigo is None or codigo.strip() == "":
        return "Invalido: codigo vacio"
    if len(codigo) != 30:
        return "Invalido: Longitud incorrecta"
    if not codigo.isdigit():
        return "Invalido: Contiene caracteres especiales"
    if codigo[0:2] != "41":
        return "Invalido: Error en codigo departamento"
    if codigo[2:5] != "013":
        return "Invalido: Error en codigo municipio"
    if codigo[9:13] != "0000":
        return "Invalido: Error en codigo barrio y comuna"
    if codigo[13:17] == "0000":
        return "Invalido: Manzana sin codigo"
    if codigo[17:21] == "0000":
        return "Invalido: Terreno sin codigo"
    if codigo[21:29] == "000000000":
        return "Invalido: Posiciones 22 a 30 deben ser '00000'"
    if codigo[21] == "9":
        return "Valido: PROPIEDAD HORIZONTAL"
    if codigo[21] == "0":
        return "Invalido: terreno FORMAL"
    if codigo[21] == "8":
        return "Valido: CONDOMINIO"
    if codigo[21] == "7":
        return "Invalido: PARQUE CEMENTERIO"
    if codigo[21] == "4":
        return "Invalido: VIAS"
    if codigo[21] == "3":
        return "Invalido: BIENES DE USO PUBLICO"
    if codigo[21] == "1":
        return "Invalido: condicion de NPN invalida"
    if codigo[21] == "5":
        return "Invalido: conidicion de NPN invalida"
    if codigo[21] == "6":
        return "Invalido: condicion de NPN invalida"
    
    return "Valido"

def validar_codigo_manzana(manzana_codigo):
    if manzana_codigo is None or manzana_codigo.strip() == "":
        return "Invalido: Codigo vacio"
    if len(manzana_codigo) != 17:
        return "Invalido: Longitud incorrecta"
    if not manzana_codigo.isdigit():
        return "Invalido: Contiene caracteres especiales"
    if manzana_codigo[0:2] != "41":
        return "Invalido: Error en codigo departamento"
    if manzana_codigo[2:5] != "013":
        return "Invalido: Error en codigo municipio"
    if manzana_codigo[13:17] == "0000":
        return "Invalido: Manzana sin codigo"
    if manzana_codigo[9:13] != "0000":
        return "Invalido: Error en codigo barrio y comuna"
    return "Valido"

def validar_codigo_anterior(codigo_anterior):
    if codigo_anterior is None or codigo_anterior.strip() == "":
        return "Invalido: Codigo vacio"
    if len(codigo_anterior) != 20:
        return "Invalido: Longitud incorrecta"
    if not codigo_anterior.isdigit():
        return "Invalido: Contiene caracteres especiales"
    if codigo_anterior[0:2] != "41":
        return "Invalido: Error en codigo departamento"
    if codigo_anterior[2:5] != "013":
        return "Invalido: Error en codigo municipio"    
    if codigo_anterior[17:20] != "000":
        return "Invalido: Las posiciones de 18 a 20 deben ser '000'"
    if codigo_anterior[9:13] == "0000":
        return "Invalido: Las posiciones de manzana no pueden ser '0000'"
    if codigo_anterior[13:17] == "0000":
        return "Invalido: Las posiciones de terreno no pueden ser '0000'"
    if codigo_anterior[19] == "9":
        return "Valido: PROPIEDAD HORIZONTAL"
    if codigo_anterior[19] == "2":
        return "Invalido: terreno INFORMAL"
    if codigo_anterior[19] == "8":
        return "Valido: CONDOMINIO"
    if codigo_anterior[19] == "7":
        return "Invalido: PARQUE CEMENTERIO"
    if codigo_anterior[19] == "4":
        return "Invalido: VIAS"
    if codigo_anterior[19] == "3":
        return "Invalido: BIEN DE USO PUBLICO"
    if codigo_anterior[19] == "1":
        return "Invalido: error en condicion de NPN"
    if codigo_anterior[19] == "5":
        return "Invalido: error en condicion de NPN"
    if codigo_anterior[19] == "6":
        return "Invalido: error en condicion de NPN"
    return "Valido"

def validar_codigo_anterior_informal(codigo_anterior):
    if codigo_anterior is None or codigo_anterior.strip() == "":
        return "Invalido: Codigo vacio"
    if len(codigo_anterior) != 20:
        return "Invalido: Longitud incorrecta"
    if not codigo_anterior.isdigit():
        return "Invalido: Contiene caracteres especiales"
    if codigo_anterior[0:2] != "41":
        return "Invalido: Error en codigo departamento"
    if codigo_anterior[2:5] != "013":
        return "Invalido: Error en codigo municipio"    
    if codigo_anterior[17:20] != "000":
        return "Invalido: Las posiciones de 18 a 20 deben ser '000'"
    if codigo_anterior[9:13] == "0000":
        return "Invalido: Las posiciones de manzana no pueden ser '0000'"
    if codigo_anterior[13:17] == "0000":
        return "Invalido: Las posiciones de terreno no pueden ser '0000'"
    if codigo_anterior[19] == "9":
        return "Valido: PROPIEDAD HORIZONTAL"
    if codigo_anterior[19] == "0":
        return "Invalido: terreno FORMAL"
    if codigo_anterior[19] == "8":
        return "Valido: CONDOMINIO"
    if codigo_anterior[19] == "7":
        return "Invalido: PARQUE CEMENTERIO"
    if codigo_anterior[19] == "4":
        return "Invalido: VIAS"
    if codigo_anterior[19] == "3":
        return "Invalido: BIEN DE USO PUBLICO"
    if codigo_anterior[19] == "1":
        return "Invalido: error en condicion de NPN"
    if codigo_anterior[19] == "5":
        return "Invalido: error en condicion de NPN"
    if codigo_anterior[19] == "6":
        return "Invalido: error en condicion de NPN"
    return "Valido"

def validar_codigo_mpio(codigo_municipio):
    if codigo_municipio is None or codigo_municipio.strip() == "":
        return "Invalido: Codigo vacio"
    if len(codigo_municipio) != 5:
        return "Invalido: Longitud incorrecta"
    if not codigo_municipio.isdigit():
        return "Invalido: Contiene caracteres especiales"
    if codigo_municipio[0:2] != "41":
        return "Invalido: Error en codigo departamento"
    if codigo_municipio[2:5] != "013":
        return "Invalido: Error en codigo municipio"
    return "Valido"

def validar_cod_ant_manzana(codant_mz):
    if codant_mz is None or codant_mz.strip() == "":
        return "Invalido: Codigo vacio"
    if len(codant_mz) != 13:
        return "Invalido: Longitud incorrecta"
    if not codant_mz.isdigit():
        return "Invalido: Contiene caracteres especiales"
    if codant_mz[0:2] != "41":
        return "Invalido: Error en codigo departamento"
    if codant_mz[2:5] != "013":
        return "Invalido: Error en codigo municipio"
    if codant_mz[9:13] == "0000":
        return "Invalido: Las posiciones de manzana no pueden ser '0000'"
    return "valido"

def validar_Uconst_etiqueta(etiqueta):
    if etiqueta is None:
        return "Valido"
    return "Invalido: la etiqueta debe ser Null"

def validar_Uconst_ident(identificador):
    if identificador is None or identificador.strip() == "":
        return "Invalido: Identificador vacio"
    if not identificador.isalpha():
        return "Invalido: Contiene caracteres especiales"
    return "valido"

def validar_unidad_etiqueta(etiqueta):
    if etiqueta is None or etiqueta.strip() == "":
        return "Invalido: Etiqueta conetener el numero"
    if len(etiqueta) != 2:
        return "Invalido: Deben ser dos digitos"
    if not etiqueta.isdigit():
        return "Invalido: Deben ser numeros"
    return "Valido"

def validar_unidad_identificador(identificador):
    if identificador is None or identificador.strip() == "":
        return "Invalido: Identificador vacio"
    if len(identificador) != 1:
        return "Invalido: Debe tener un solo caracter"
    if not identificador.isalpha():
        return "Invalido: Contiene caracteres especiales"
    return "Valido"

def validar_direccion(direccion):
    if direccion is None or (direccion).strip() == "":
        return "Invalido: campo vacio"
    if not re.match("^[a-zA-Z0-9\s]+$", direccion):
        return "Invalido: contiene caracteres especiales"
    return "Valido"
    
def campos_terreno(layer, field1, field2):
    resultados=[]
    with arcpy.da.SearchCursor(layer, [field1, field2]) as cursor:
        for codigo, manzana_codigo in cursor:
            if codigo is None or manzana_codigo is None or codigo.strip() == "" or manzana_codigo.strip() == "":
                estado = "Invalido: Codigos vacios"
            elif codigo[0:17] == manzana_codigo:
                estado = "Valido"
            else:
                estado = "Invalido: codigo y manzana codigo no corresponden"
            resultados.append((codigo,estado))
    return resultados

def campos_construccion(layer, field1, field2):
    resultados=[]
    with arcpy.da.SearchCursor(layer, [field1, field2]) as cursor:
        for codigo, construccion_codigo in cursor:
            if codigo is None or construccion_codigo is None or codigo.strip() == "" or construccion_codigo.strip() == "":
                estado = "Invalido: Codigos vacios"
            elif codigo == construccion_codigo:
                estado = "Valido"
            else :
                estado = "Invalido: codigo y terreno codigo no corresponden"
            resultados.append((codigo,estado))
    return resultados

def campos_unidad(layer, field1, field2, field3):
    resultados=[]
    with arcpy.da.SearchCursor(layer, [field1, field2, field3]) as cursor:
        for codigo, construccion_codigo, unidad_codigo in cursor:
            if codigo is None or construccion_codigo is None or unidad_codigo is None or codigo.strip() == "" or construccion_codigo.strip() == "" or unidad_codigo.strip() == "":
                estado = "Invalido: Codigos vacios"
            elif codigo[0:21] == construccion_codigo[0:21] == unidad_codigo[0:21]:
                estado = "Valido"
            else:
                estado = "Invalido: codigo, construccion codigo y unidad codigo no corresponden en la capa"
            resultados.append((codigo,estado))
    return resultados

def intersect(layer, terreno, construccion, construccion_terreno, unidad, unidad_terreno, unidad_construccion):
    resultados = []
    with arcpy.da.SearchCursor(layer, [terreno, construccion, construccion_terreno, unidad, unidad_terreno, unidad_construccion]) as cursor:
        for codigot, codigoc, construccionc, codigou, unidadt, unidadc in cursor:
            if codigot is None or codigoc is None or construccionc is None or codigou is None or unidadt is None or unidadc is None or codigot.strip() == "" or codigoc.strip() == "" or codigou.strip() == "" or unidadt.strip() == "" or unidadc.strip() == "":
                estado = "Invalido: Codigos vacios"
            elif codigot[0:21] == codigoc[0:21] == construccionc[0:21] == codigou[0:21] == unidadt[0:21] == unidadc[0:21]:
                estado = "valido"
            else:
                estado = "Invalido: uno de los codigos de unidad, construccion y terreno en el INTERSECT no corresponden"
            resultados.append((codigot,estado))
    return resultados   

def intersect_manzana(layer, terreno, construccion, construccion_terreno, unidad, unidad_Terreno, unidad_construccion, manzana):
    resultado = []
    with arcpy.da.SearchCursor(layer, [terreno,construccion,construccion_terreno,unidad, unidad_Terreno, unidad_construccion, manzana]) as cursor:
        for codigot, codigoc, construccionc, codigou, unidadt, unidadc, manzana in cursor:
            if codigot is None or codigoc is None or construccionc is None or codigou is None or unidadt is None or unidadc is None or manzana is None or codigot.strip() == "" or codigoc.strip() == "" or codigou.strip() == "" or unidadt.strip() == "" or unidadc.strip() == "" or manzana.strip() == "":
                estado = "Invalido: Codigos vacios"
            elif codigot[0:17] == codigoc[0:17] == construccionc[0:17] == codigou[0:17] == unidadt[0:17] == unidadc[0:17] == manzana:
                estado = "valido"
            else:
                estado = "Invalido: uno de los codigos de unidad, construccion y terreno en el INTERSECT no corresponden a la manzana"
            resultado.append((codigot,estado))
    return resultado



# FUNCION PROCESAR DATOS
def data_process(layer, field, validar_funcion):
    with arcpy.da.SearchCursor(layer, [field]) as cursor:
        return [(row[0], validar_funcion(row[0])) for row in cursor]


codigo_terrenos = data_process(terrenoctm12, "CODIGO", validar_codigo)
manzana_terrenos = data_process(terrenoctm12, "MANZANA_CODIGO", validar_codigo_manzana)
codigo_anterior_terrenos = data_process(terrenoctm12, "CODIGO_ANTERIOR", validar_codigo_anterior)
codigo_municipio = data_process(terrenoctm12, "CODIGO_MUNICIPIO", validar_codigo_mpio)
codigo_construcciones = data_process(construccionctm12, "CODIGO", validar_codigo)
construccion_terreno = data_process(construccionctm12, "TERRENO_CODIGO", validar_codigo)
construccion_municipio= data_process(construccionctm12, "CODIGO_MUNICIPIO", validar_codigo_mpio)
construccion_etiqueta = data_process(construccionctm12, "ETIQUETA", validar_Uconst_etiqueta)
construccion_identificador = data_process(construccionctm12, "IDENTIFICADOR", validar_Uconst_ident)
construccion_antiguo = data_process(construccionctm12, "CODIGO_ANTERIOR", validar_codigo_anterior)
unidad_codigo = data_process(unidadconstruccionctm12, "CODIGO", validar_codigo)
unidad_terreno = data_process(unidadconstruccionctm12, "TERRENO_CODIGO" , validar_codigo)
unidad_construccion = data_process(unidadconstruccionctm12, "CONSTRUCCION_CODIGO" , validar_codigo)
unidad_municipio = data_process(unidadconstruccionctm12, "CODIGO_MUNICIPIO", validar_codigo_mpio)
unidad_etiqueta = data_process(unidadconstruccionctm12, "ETIQUETA", validar_unidad_etiqueta)
unidada_identificador = data_process(unidadconstruccionctm12, "IDENTIFICADOR", validar_unidad_identificador)
nomeclatura_codigo = data_process(nomeclaturadom, "TERRENO_CODIGO", validar_codigo)
nomenclatura_direccion = data_process(nomeclaturadom, "TEXTO", validar_direccion)
manzana_codigo = data_process(manzanactm12, "CODIGO", validar_codigo_manzana)
manzana_codigo_anterior = data_process(manzanactm12, "CODIGO_ANTERIOR", validar_cod_ant_manzana)
manzana_municipio = data_process(manzanactm12, "CODIGO_MUNICIPIO", validar_codigo_mpio)
#correspondencia
correspondencia_terreno = campos_terreno(terrenoctm12, "CODIGO", "MANZANA_CODIGO")
correspondecia_construccion = campos_construccion(construccionctm12, "CODIGO", "TERRENO_CODIGO")
correspondencia_unidad = campos_unidad(unidadconstruccionctm12, "CODIGO", "TERRENO_CODIGO","CONSTRUCCION_CODIGO")
#Geometrias
intersect_tcu = intersect(intersectctm12, "CODIGO_12","CODIGO_1","TERRENO_CODIGO_1", "CODIGO", "TERRENO_CODIGO","CONSTRUCCION_CODIGO")
intersect_man = intersect_manzana (intersectctm12, "CODIGO_12","CODIGO_1","TERRENO_CODIGO_1", "CODIGO", "TERRENO_CODIGO","CONSTRUCCION_CODIGO","CODIGO_12_13")

# GUARDAR EN CSV
with open(output_csv, 'wb') as file:
    writer = csv.writer(file)
    writer.writerow(["CODIGO", "CAPA", "ESTADO"])
    
    def escribir_resultados(data, capa):
        for codigo, estado in data:
            writer.writerow([codigo if codigo is not None else "vacio", capa, estado])
    
    
    escribir_resultados(codigo_terrenos, "Terreno_codigo")
    escribir_resultados(manzana_terrenos, "Terreno_manzana")
    escribir_resultados(codigo_anterior_terrenos, "Terreno_codigo_anterior")
    escribir_resultados(codigo_municipio, "Terreno_codigo_municipio")
    escribir_resultados(correspondencia_terreno, "Terreno_correspondecia")
    
    escribir_resultados(codigo_construcciones, "Uconstruccion_codigo")
    escribir_resultados(construccion_terreno, "Uconstruccion_terreno")
    escribir_resultados(construccion_municipio, "Uconstruccion_codigo_municipio")
    escribir_resultados(construccion_etiqueta, "Uconstruccion_etiqueta")
    escribir_resultados(construccion_identificador, "Uconstruccion_identificador")
    escribir_resultados(correspondecia_construccion, "Uconstruccion_correspondencia")
    escribir_resultados(construccion_antiguo, "Uconstruccion_codigoanterior")
    
    escribir_resultados(unidad_codigo, "Unidad_codigo")
    escribir_resultados(unidad_terreno, "Unidad_terreno")
    escribir_resultados(unidad_construccion, "Unidad_construccion")
    escribir_resultados(unidad_municipio, "Unidad_codigo_municipio")
    escribir_resultados(unidad_etiqueta, "Unidad_etiqueta")
    escribir_resultados(unidada_identificador, "Unidad_identificador")
    escribir_resultados(correspondencia_unidad, "Unidad_correspondencia")
    
    escribir_resultados(nomeclatura_codigo, "Nomeclatura_domic_codigo")
    escribir_resultados(nomenclatura_direccion, "Nomeclatura_domic_direccion")
    escribir_resultados(manzana_codigo, "Manzana_codigo")
    escribir_resultados(manzana_codigo_anterior, "Manzana_codigo_anterior")
    escribir_resultados(manzana_municipio, "Manzana_codigo_municipio")

    escribir_resultados(intersect_tcu,"Terreno_Construccion_Unidad")
    escribir_resultados(intersect_man, "Manzana_terreno_construccion_unidad")

       
    


#ELABORADO POR IVAN PINZA
print("Resultados exportados a:", output_csv)
arcpy.AddWarning("Proceso finalizado con exito, resutlados exportados a C:\temp\resultados_validacion.csv")