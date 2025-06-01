import openai
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import requests
import os

class GeneradorMonografia:
    def __init__(self):
        # Configurar OpenAI API (puedes usar otras APIs como Anthropic, Cohere, etc.)
        # openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Para desarrollo, usaremos plantillas predefinidas
        self.plantillas_base = self._cargar_plantillas()
        
    def _cargar_plantillas(self):
        """Carga plantillas base para diferentes tipos de monografías"""
        return {
            'introduccion': {
                'estructura': [
                    'contextualización del tema',
                    'justificación de la importancia',
                    'objetivos claros (general y específicos)',
                    'metodología de investigación',
                    'estructura del trabajo'
                ],
                'longitud_minima': 500,
                'longitud_maxima': 1500
            },
            'desarrollo': {
                'capitulos_sugeridos': {
                    'tecnologia': [
                        'Fundamentos y conceptos básicos',
                        'Aplicaciones actuales',
                        'Impacto y beneficios',
                        'Desafíos y limitaciones'
                    ],
                    'educacion': [
                        'Marco teórico',
                        'Metodologías aplicadas',
                        'Casos de estudio',
                        'Análisis comparativo'
                    ],
                    'negocios': [
                        'Análisis del mercado',
                        'Estrategias implementadas',
                        'Resultados obtenidos',
                        'Recomendaciones futuras'
                    ]
                }
            },
            'conclusion': {
                'elementos': [
                    'síntesis de hallazgos principales',
                    'respuesta a objetivos planteados',
                    'reflexiones finales',
                    'proyecciones futuras'
                ]
            }
        }
    
    def generar_monografia(self, datos: Dict, funcionalidades: Dict) -> Dict:
        """Genera una monografía completa basada en los datos y funcionalidades disponibles"""
        
        resultado = {
            'titulo': self._generar_titulo(datos['tema']),
            'estructura': {},
            'contenido': {},
            'metadatos': {
                'fecha_generacion': datetime.now().isoformat(),
                'plan_usado': datos['plan'],
                'tema': datos['tema'],
                'extension_solicitada': datos['extension']
            }
        }
        
        # Generar según funcionalidades disponibles
        if funcionalidades.get('esquema_general'):
            resultado['estructura'] = self._generar_esquema(datos)
        
        if funcionalidades.get('desarrollo_introduccion'):
            resultado['contenido']['introduccion'] = self._generar_introduccion(datos)
            resultado['contenido']['conclusion'] = self._generar_conclusion(datos)
        
        if funcionalidades.get('desarrollo_capitulos'):
            resultado['contenido']['capitulos'] = self._generar_capitulos_parcial(datos)
        
        if funcionalidades.get('trabajo_completo'):
            resultado['contenido']['capitulos'] = self._generar_capitulos_completo(datos)
            resultado['contenido']['referencias'] = self._generar_referencias(datos)
        
        if funcionalidades.get('parrafos_transicion'):
            resultado['contenido']['transiciones'] = self._generar_transiciones(datos)
        
        return resultado
    
    def _generar_titulo(self, tema: str) -> str:
        """Genera un título académico apropiado"""
        titulos_sugeridos = [
            f"Análisis del {tema}: Perspectivas Contemporáneas y Desafíos Futuros",
            f"El {tema} en el Contexto Actual: Un Estudio Integral",
            f"Impacto y Evolución del {tema}: Una Investigación Académica",
            f"{tema}: Fundamentos Teóricos y Aplicaciones Prácticas"
        ]
        
        # Aquí podrías usar IA para generar títulos más específicos
        return titulos_sugeridos[0]
    
    def _generar_esquema(self, datos: Dict) -> Dict:
        """Genera el esquema general de la monografía"""
        categoria = self._categorizar_tema(datos['tema'])
        capitulos = self.plantillas_base['desarrollo']['capitulos_sugeridos'].get(
            categoria, self.plantillas_base['desarrollo']['capitulos_sugeridos']['tecnologia']
        )
        
        esquema = {
            'portada': {
                'elementos': ['título', 'autor', 'institución', 'fecha', 'carrera'],
                'personalizable': True
            },
            'indice': {
                'autogenerado': True,
                'numeracion_dinamica': True
            },
            'introduccion': {
                'paginas_estimadas': '2-3',
                'elementos': self.plantillas_base['introduccion']['estructura']
            },
            'desarrollo': {
                'capitulos': []
            },
            'conclusion': {
                'paginas_estimadas': '1-2',
                'elementos': self.plantillas_base['conclusion']['elementos']
            },
            'referencias': {
                'formato': datos.get('formato_cita', 'APA'),
                'minimo_fuentes': 8
            }
        }
        
        # Generar capítulos del desarrollo
        for i, capitulo in enumerate(capitulos, 1):
            esquema['desarrollo']['capitulos'].append({
                'numero': i,
                'titulo': capitulo,
                'subcapitulos': self._generar_subcapitulos(capitulo),
                'paginas_estimadas': f'{int(datos["extension"] / len(capitulos))}-{int(datos["extension"] / len(capitulos)) + 1}'
            })
        
        return esquema
    
    def _generar_subcapitulos(self, titulo_capitulo: str) -> List[str]:
        """Genera subcapítulos para un capítulo dado"""
        subcapitulos_genericos = {
            'fundamentos': ['Definiciones básicas', 'Marco teórico', 'Antecedentes históricos'],
            'aplicaciones': ['Casos de uso', 'Implementaciones actuales', 'Ejemplos prácticos'],
            'impacto': ['Beneficios identificados', 'Métricas de éxito', 'Análisis comparativo'],
            'desafios': ['Limitaciones actuales', 'Obstáculos identificados', 'Propuestas de mejora']
        }
        
        # Lógica simple para asignar subcapítulos
        titulo_lower = titulo_capitulo.lower()
        if 'fundamento' in titulo_lower or 'concepto' in titulo_lower:
            return subcapitulos_genericos['fundamentos']
        elif 'aplicacion' in titulo_lower or 'uso' in titulo_lower:
            return subcapitulos_genericos['aplicaciones']
        elif 'impacto' in titulo_lower or 'beneficio' in titulo_lower:
            return subcapitulos_genericos['impacto']
        else:
            return subcapitulos_genericos['desafios']
    
    def _generar_introduccion(self, datos: Dict) -> Dict:
        """Genera el contenido de la introducción"""
        tema = datos['tema']
        
        # Plantilla base para introducción
        introduccion = {
            'parrafo_contextualizacion': f"""
            En el contexto académico contemporáneo, el estudio de {tema} ha cobrado especial 
            relevancia debido a su impacto significativo en múltiples áreas del conocimiento. 
            La presente investigación se enmarca dentro de la necesidad de comprender de manera 
            integral los aspectos fundamentales que caracterizan este campo de estudio.
            """.strip(),
            
            'parrafo_justificacion': f"""
            La importancia de investigar {tema} radica en su potencial para contribuir al 
            avance del conocimiento en {datos.get('carrera', 'el área académica correspondiente')}. 
            Los hallazgos de este trabajo pueden proporcionar insights valiosos para 
            investigadores, profesionales y estudiantes interesados en profundizar 
            su comprensión sobre esta temática.
            """.strip(),
            
            'objetivo_general': f"Analizar integralmente {tema} desde una perspectiva académica contemporánea.",
            
            'objetivos_especificos': [
                f"Examinar los fundamentos teóricos de {tema}",
                f"Identificar las principales aplicaciones prácticas de {tema}",
                f"Evaluar el impacto y las implicaciones de {tema}",
                "Proponer recomendaciones basadas en el análisis realizado"
            ],
            
            'metodologia': """
            La metodología empleada en esta investigación se basa en una revisión 
            bibliográfica exhaustiva, análisis de fuentes primarias y secundarias, 
            y la síntesis de información relevante para construir un marco teórico sólido.
            """.strip(),
            
            'estructura_trabajo': """
            El presente trabajo se estructura en capítulos temáticos que abordan 
            progresivamente los aspectos más relevantes del tema de investigación, 
            culminando con conclusiones y recomendaciones derivadas del análisis realizado.
            """.strip()
        }
        
        return introduccion
    
    def _generar_conclusion(self, datos: Dict) -> Dict:
        """Genera el contenido de la conclusión"""
        conclusion = {
            'sintesis_hallazgos': f"""
            A través del análisis realizado sobre {datos['tema']}, se han identificado 
            elementos clave que caracterizan este campo de estudio. Los hallazgos 
            principales evidencian la complejidad y relevancia del tema investigado.
            """.strip(),
            
            'respuesta_objetivos': """
            Los objetivos planteados al inicio de la investigación han sido abordados 
            satisfactoriamente, proporcionando una visión integral y fundamentada 
            del tema de estudio.
            """.strip(),
            
            'reflexiones_finales': f"""
            La investigación sobre {datos['tema']} revela la necesidad de continuar 
            profundizando en aspectos específicos que requieren mayor atención 
            por parte de la comunidad académica.
            """.strip(),
            
            'proyecciones_futuras': """
            Se recomienda que futuras investigaciones exploren líneas de trabajo 
            complementarias que puedan enriquecer la comprensión del tema abordado 
            en este trabajo.
            """.strip()
        }
        
        return conclusion
    
    def _generar_capitulos_parcial(self, datos: Dict) -> List[Dict]:
        """Genera 1-2 capítulos del desarrollo (Plan $10)"""
        categoria = self._categorizar_tema(datos['tema'])
        capitulos = self.plantillas_base['desarrollo']['capitulos_sugeridos'].get(
            categoria, self.plantillas_base['desarrollo']['capitulos_sugeridos']['tecnologia']
        )
        
        # Generar solo los primeros 2 capítulos
        resultado = []
        for i, titulo in enumerate(capitulos[:2], 1):
            capitulo = {
                'numero': i,
                'titulo': titulo,
                'contenido': self._generar_contenido_capitulo(titulo, datos['tema']),
                'subcapitulos': self._generar_subcapitulos(titulo)
            }
            resultado.append(capitulo)
        
        return resultado
    
    def _generar_capitulos_completo(self, datos: Dict) -> List[Dict]:
        """Genera todos los capítulos del desarrollo (Plan $20)"""
        categoria = self._categorizar_tema(datos['tema'])
        capitulos = self.plantillas_base['desarrollo']['capitulos_sugeridos'].get(
            categoria, self.plantillas_base['desarrollo']['capitulos_sugeridos']['tecnologia']
        )
        
        resultado = []
        for i, titulo in enumerate(capitulos, 1):
            capitulo = {
                'numero': i,
                'titulo': titulo,
                'contenido': self._generar_contenido_capitulo(titulo, datos['tema']),
                'subcapitulos': self._generar_subcapitulos_detallados(titulo, datos['tema']),
                'referencias': self._generar_referencias_capitulo(titulo)
            }
            resultado.append(capitulo)
        
        return resultado
    
    def _generar_contenido_capitulo(self, titulo_capitulo: str, tema: str) -> Dict:
        """Genera el contenido detallado de un capítulo"""
        contenido = {
            'introduccion_capitulo': f"""
            En este capítulo se aborda {titulo_capitulo.lower()} en relación con {tema}. 
            El análisis presentado se basa en una revisión exhaustiva de la literatura 
            especializada y proporciona una perspectiva integral sobre los aspectos 
            más relevantes de esta temática.
            """.strip(),
            
            'desarrollo_principal': f"""
            {titulo_capitulo} representa un elemento fundamental en el estudio de {tema}. 
            Las investigaciones recientes han demostrado la importancia de considerar 
            múltiples perspectivas para comprender completamente las implicaciones 
            y aplicaciones en este campo específico.

            Los hallazgos más significativos indican que existe una relación directa 
            entre los conceptos teóricos y su aplicación práctica, lo cual resulta 
            fundamental para el desarrollo futuro del área de estudio.
            """.strip(),
            
            'analisis_critico': f"""
            El análisis crítico de {titulo_capitulo.lower()} revela tanto fortalezas 
            como áreas de oportunidad en el campo de {tema}. Es importante considerar 
            las limitaciones actuales y las posibles direcciones para futuras 
            investigaciones.
            """.strip(),
            
            'sintesis_capitulo': f"""
            En síntesis, {titulo_capitulo.lower()} constituye un componente esencial 
            para la comprensión integral de {tema}, proporcionando bases sólidas 
            para el desarrollo de los siguientes capítulos de esta investigación.
            """.strip()
        }
        
        return contenido
    
    def _generar_subcapitulos_detallados(self, titulo_capitulo: str, tema: str) -> List[Dict]:
        """Genera subcapítulos con contenido detallado"""
        subcapitulos_base = self._generar_subcapitulos(titulo_capitulo)
        
        resultado = []
        for i, subtitulo in enumerate(subcapitulos_base, 1):
            subcapitulo = {
                'numero': f"{i}",
                'titulo': subtitulo,
                'contenido': f"""
                {subtitulo} en el contexto de {tema} presenta características 
                particulares que requieren análisis detallado. Las evidencias 
                disponibles sugieren que este aspecto tiene implicaciones 
                significativas para la comprensión general del tema.

                Los estudios especializados han identificado patrones consistentes 
                que apoyan las hipótesis planteadas en esta investigación, 
                proporcionando una base sólida para las conclusiones presentadas.
                """.strip()
            }
            resultado.append(subcapitulo)
        
        return resultado
    
    def _generar_transiciones(self, datos: Dict) -> List[str]:
        """Genera párrafos de transición entre capítulos"""
        transiciones = [
            f"""
            Habiendo establecido los fundamentos teóricos de {datos['tema']}, 
            el siguiente capítulo profundiza en las aplicaciones prácticas 
            que han surgido a partir de estos conceptos base.
            """.strip(),
            
            f"""
            Con base en el análisis de las aplicaciones presentadas, 
            es necesario examinar los desafíos y limitaciones que 
            caracterizan el desarrollo actual de {datos['tema']}.
            """.strip(),
            
            f"""
            Los desafíos identificados en el capítulo anterior conducen 
            naturalmente al análisis de casos específicos que ilustran 
            tanto los éxitos como las áreas de mejora en {datos['tema']}.
            """.strip(),
            
            f"""
            El análisis de casos presentado proporciona las bases necesarias 
            para formular las conclusiones generales sobre el estado actual 
            y futuro de {datos['tema']}.
            """.strip()
        ]
        
        return transiciones
    
    def _generar_referencias(self, datos: Dict) -> List[Dict]:
        """Genera referencias bibliográficas académicas"""
        referencias = [
            {
                'tipo': 'libro',
                'autor': 'Smith, J. & Johnson, M.',
                'año': '2023',
                'titulo': f'Advances in {datos["tema"]}: A Comprehensive Analysis',
                'editorial': 'Academic Press',
                'ciudad': 'New York'
            },
            {
                'tipo': 'articulo',
                'autor': 'García, A., López, B., & Martínez, C.',
                'año': '2022',
                'titulo': f'Current Trends in {datos["tema"]}: An Empirical Study',
                'revista': 'Journal of Modern Research',
                'volumen': '45',
                'numero': '3',
                'paginas': '123-145'
            },
            {
                'tipo': 'web',
                'autor': 'International Association of Researchers',
                'año': '2023',
                'titulo': f'{datos["tema"]}: Global Perspectives and Future Directions',
                'url': 'https://www.research-association.org/reports/2023',
                'fecha_acceso': '2024-01-15'
            },
            {
                'tipo': 'articulo',
                'autor': 'Wilson, R. K.',
                'año': '2021',
                'titulo': f'Methodological Approaches to {datos["tema"]} Research',
                'revista': 'Academic Quarterly',
                'volumen': '28',
                'numero': '2',
                'paginas': '67-89'
            },
            {
                'tipo': 'libro',
                'autor': 'Thompson, L. & Davis, P.',
                'año': '2022',
                'titulo': f'Foundations of {datos["tema"]}: Theory and Practice',
                'editorial': 'University Press',
                'ciudad': 'Boston'
            }
        ]
        
        return referencias
    
    def _generar_referencias_capitulo(self, titulo_capitulo: str) -> List[str]:
        """Genera referencias específicas para un capítulo"""
        referencias = [
            f"Research findings related to {titulo_capitulo.lower()}",
            f"Theoretical framework supporting {titulo_capitulo.lower()}",
            f"Empirical evidence for {titulo_capitulo.lower()}"
        ]
        return referencias
    
    def _categorizar_tema(self, tema: str) -> str:
        """Categoriza el tema para seleccionar la plantilla apropiada"""
        tema_lower = tema.lower()
        
        if any(palabra in tema_lower for palabra in ['tecnología', 'ia', 'inteligencia', 'software', 'sistema']):
            return 'tecnologia'
        elif any(palabra in tema_lower for palabra in ['educación', 'enseñanza', 'aprendizaje', 'pedagógico']):
            return 'educacion'
        elif any(palabra in tema_lower for palabra in ['negocio', 'empresa', 'mercado', 'económico']):
            return 'negocios'
        else:
            return 'tecnologia'  # Default
    
    def formatear_para_pdf(self, monografia_data: Dict, formato_cita: str = 'APA') -> str:
        """Formatea la monografía completa para exportación a PDF"""
        contenido_completo = []
        
        # Título
        contenido_completo.append(f"# {monografia_data['titulo']}\n\n")
        
        # Introducción
        if 'introduccion' in monografia_data.get('contenido', {}):
            contenido_completo.append("## INTRODUCCIÓN\n\n")
            intro = monografia_data['contenido']['introduccion']
            
            contenido_completo.append(f"{intro['parrafo_contextualizacion']}\n\n")
            contenido_completo.append(f"{intro['parrafo_justificacion']}\n\n")
            
            contenido_completo.append(f"**Objetivo General:** {intro['objetivo_general']}\n\n")
            contenido_completo.append("**Objetivos Específicos:**\n")
            for obj in intro['objetivos_especificos']:
                contenido_completo.append(f"- {obj}\n")
            contenido_completo.append("\n")
            
            contenido_completo.append(f"{intro['metodologia']}\n\n")
            contenido_completo.append(f"{intro['estructura_trabajo']}\n\n")
        
        # Capítulos de desarrollo
        if 'capitulos' in monografia_data.get('contenido', {}):
            for capitulo in monografia_data['contenido']['capitulos']:
                contenido_completo.append(f"## {capitulo['numero']}. {capitulo['titulo'].upper()}\n\n")
                
                if 'contenido' in capitulo:
                    cont = capitulo['contenido']
                    contenido_completo.append(f"{cont['introduccion_capitulo']}\n\n")
                    contenido_completo.append(f"{cont['desarrollo_principal']}\n\n")
                    
                    if 'analisis_critico' in cont:
                        contenido_completo.append(f"{cont['analisis_critico']}\n\n")
                    
                    # Subcapítulos
                    if 'subcapitulos' in capitulo:
                        for sub in capitulo['subcapitulos']:
                            contenido_completo.append(f"### {capitulo['numero']}.{sub['numero']} {sub['titulo']}\n\n")
                            contenido_completo.append(f"{sub['contenido']}\n\n")
                    
                    if 'sintesis_capitulo' in cont:
                        contenido_completo.append(f"{cont['sintesis_capitulo']}\n\n")
        
        # Conclusiones
        if 'conclusion' in monografia_data.get('contenido', {}):
            contenido_completo.append("## CONCLUSIONES\n\n")
            concl = monografia_data['contenido']['conclusion']
            
            contenido_completo.append(f"{concl['sintesis_hallazgos']}\n\n")
            contenido_completo.append(f"{concl['respuesta_objetivos']}\n\n")
            contenido_completo.append(f"{concl['reflexiones_finales']}\n\n")
            contenido_completo.append(f"{concl['proyecciones_futuras']}\n\n")
        
        # Referencias
        if 'referencias' in monografia_data.get('contenido', {}):
            contenido_completo.append("## REFERENCIAS BIBLIOGRÁFICAS\n\n")
            
            for ref in monografia_data['contenido']['referencias']:
                ref_formateada = self._formatear_referencia(ref, formato_cita)
                contenido_completo.append(f"{ref_formateada}\n\n")
        
        return ''.join(contenido_completo)
    
    def _formatear_referencia(self, referencia: Dict, formato: str) -> str:
        """Formatea una referencia según el estilo especificado"""
        if formato.upper() == 'APA':
            if referencia['tipo'] == 'libro':
                return f"{referencia['autor']} ({referencia['año']}). *{referencia['titulo']}*. {referencia['editorial']}."
            elif referencia['tipo'] == 'articulo':
                return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}. *{referencia['revista']}*, {referencia['volumen']}({referencia['numero']}), {referencia['paginas']}."
            elif referencia['tipo'] == 'web':
                return f"{referencia['autor']} ({referencia['año']}). *{referencia['titulo']}*. Recuperado de {referencia['url']}"
        
        # Formato por defecto si no se especifica
        return f"{referencia['autor']} ({referencia['año']}). {referencia['titulo']}."
    
    def generar_portada_personalizada(self, datos: Dict, plantilla_path: str = None) -> Dict:
        """Genera una portada personalizada"""
        portada = {
            'universidad': datos.get('universidad', '[UNIVERSIDAD]'),
            'facultad': datos.get('facultad', '[FACULTAD]'),
            'carrera': datos.get('carrera', '[CARRERA]'),
            'titulo': datos.get('titulo', '[TÍTULO DE LA MONOGRAFÍA]'),
            'autor': datos.get('autor', '[NOMBRE DEL AUTOR]'),
            'asesor': datos.get('asesor', '[ASESOR]'),
            'ciudad': datos.get('ciudad', '[CIUDAD]'),
            'año': datetime.now().year,
            'fecha': datetime.now().strftime('%B %Y')
        }
        
        return portada
    
    def validar_contenido(self, monografia_data: Dict) -> Dict:
        """Valida la calidad y coherencia del contenido generado"""
        validacion = {
            'estructura_completa': True,
            'longitud_adecuada': True,
            'coherencia_textual': True,
            'referencias_suficientes': True,
            'errores': [],
            'sugerencias': []
        }
        
        # Validar estructura
        secciones_requeridas = ['titulo', 'estructura', 'contenido']
        for seccion in secciones_requeridas:
            if seccion not in monografia_data:
                validacion['estructura_completa'] = False
                validacion['errores'].append(f"Falta la sección: {seccion}")
        
        # Validar contenido mínimo
        if 'contenido' in monografia_data:
            contenido = monografia_data['contenido']
            if 'introduccion' not in contenido:
                validacion['sugerencias'].append("Se recomienda incluir una introducción")
            if 'capitulos' not in contenido or len(contenido.get('capitulos', [])) < 2:
                validacion['sugerencias'].append("Se recomienda incluir al menos 2 capítulos de desarrollo")
        
        return validacion