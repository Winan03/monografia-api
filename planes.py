class PlanesManager:
    def __init__(self):
        self.planes = {
            'gratis': {
                'nombre': 'Plan Gratuito',
                'precio': 0,
                'descripcion': 'Herramientas básicas para empezar',
                'funcionalidades': {
                    'esquema_general': True,
                    'subir_pdf': True,
                    'plantilla_portada': True,
                    'desarrollo_introduccion': False,
                    'parrafos_transicion': False,
                    'desarrollo_capitulos': False,
                    'portada_personalizada': False,
                    'edicion_online': False,
                    'guardar_versiones': False,
                    'revision_estilo': False,
                    'trabajo_completo': False
                },
                'limitaciones': {
                    'max_paginas': 5,
                    'max_archivos_mes': 3,
                    'soporte': 'comunidad'
                }
            },
            '5': {
                'nombre': 'Plan Básico ($5/mes)',
                'precio': 5,
                'descripcion': 'Asistencia básica para monografías',
                'funcionalidades': {
                    'esquema_general': True,
                    'subir_pdf': True,
                    'plantilla_portada': True,
                    'desarrollo_introduccion': True,
                    'parrafos_transicion': True,
                    'portada_personalizada': True,
                    'formato_referencias': True,
                    'revision_coherencia': True,
                    'desarrollo_capitulos': False,
                    'edicion_online': False,
                    'guardar_versiones': False,
                    'revision_estilo': False,
                    'trabajo_completo': False
                },
                'limitaciones': {
                    'max_paginas': 12,
                    'max_archivos_mes': 10,
                    'soporte': 'email'
                }
            },
            '10': {
                'nombre': 'Plan Intermedio ($10/mes)',
                'precio': 10,
                'descripcion': 'Desarrollo intermedio con más funciones',
                'funcionalidades': {
                    'esquema_general': True,
                    'subir_pdf': True,
                    'plantilla_portada': True,
                    'desarrollo_introduccion': True,
                    'parrafos_transicion': True,
                    'desarrollo_capitulos': True,
                    'portada_personalizada': True,
                    'formato_referencias': True,
                    'revision_coherencia': True,
                    'analisis_critico': True,
                    'busqueda_fuentes': True,
                    'edicion_online': True,
                    'guardar_versiones': True,
                    'revision_estilo': False,
                    'trabajo_completo': False
                },
                'limitaciones': {
                    'max_paginas': 25,
                    'max_archivos_mes': 25,
                    'soporte': 'chat'
                }
            },
            '20': {
                'nombre': 'Plan Completo ($20/mes)',
                'precio': 20,
                'descripcion': 'Servicio completo profesional',
                'funcionalidades': {
                    'esquema_general': True,
                    'subir_pdf': True,
                    'plantilla_portada': True,
                    'desarrollo_introduccion': True,
                    'parrafos_transicion': True,
                    'desarrollo_capitulos': True,
                    'trabajo_completo': True,
                    'portada_personalizada': True,
                    'formato_referencias': True,
                    'revision_coherencia': True,
                    'analisis_critico': True,
                    'busqueda_fuentes': True,
                    'edicion_online': True,
                    'guardar_versiones': True,
                    'revision_estilo': True,
                    'deteccion_plagio': True,
                    'preparacion_presentacion': True
                },
                'limitaciones': {
                    'max_paginas': 50,
                    'max_archivos_mes': 'ilimitado',
                    'soporte': 'prioritario'
                }
            }
        }
    
    def get_planes(self):
        """Retorna todos los planes disponibles"""
        return self.planes
    
    def get_plan(self, plan_id):
        """Retorna un plan específico"""
        return self.planes.get(plan_id)
    
    def get_funcionalidades_plan(self, plan_id):
        """Retorna las funcionalidades de un plan específico"""
        plan = self.planes.get(plan_id, self.planes['gratis'])
        return plan['funcionalidades']
    
    def validar_limite_paginas(self, plan_id, num_paginas):
        """Valida si el número de páginas está dentro del límite del plan"""
        plan = self.planes.get(plan_id, self.planes['gratis'])
        max_paginas = plan['limitaciones']['max_paginas']
        return num_paginas <= max_paginas
    
    def puede_usar_funcionalidad(self, plan_id, funcionalidad):
        """Verifica si el plan puede usar una funcionalidad específica"""
        funcionalidades = self.get_funcionalidades_plan(plan_id)
        return funcionalidades.get(funcionalidad, False)
    
    def get_comparacion_planes(self):
        """Retorna una comparación de funcionalidades entre planes"""
        funcionalidades_todas = set()
        
        # Recopilar todas las funcionalidades
        for plan in self.planes.values():
            funcionalidades_todas.update(plan['funcionalidades'].keys())
        
        comparacion = {}
        for func in funcionalidades_todas:
            comparacion[func] = {}
            for plan_id, plan in self.planes.items():
                comparacion[func][plan_id] = plan['funcionalidades'].get(func, False)
        
        return comparacion
    
    def get_precio_plan(self, plan_id):
        """Retorna el precio de un plan"""
        plan = self.planes.get(plan_id)
        return plan['precio'] if plan else 0

# Funcionalidades específicas por plan
FUNCIONALIDADES_DESCRIPCION = {
    'esquema_general': 'Generar esquema general de monografía',
    'subir_pdf': 'Subir PDF inicial para análisis',
    'plantilla_portada': 'Plantilla básica de portada e índice',
    'desarrollo_introduccion': 'Desarrollo de introducción y conclusión',
    'parrafos_transicion': 'Párrafos de transición entre capítulos',
    'desarrollo_capitulos': 'Desarrollo completo de 1-2 capítulos temáticos',
    'trabajo_completo': 'Desarrollo completo de toda la monografía',
    'portada_personalizada': 'Subir portada personalizada (.docx)',
    'formato_referencias': 'Formato completo de referencias bibliográficas',
    'revision_coherencia': 'Revisión de coherencia textual básica',
    'analisis_critico': 'Análisis crítico profundo del tema',
    'busqueda_fuentes': 'Búsqueda especializada de fuentes académicas',
    'edicion_online': 'Edición del documento en línea',
    'guardar_versiones': 'Guardado de versiones intermedias',
    'revision_estilo': 'Revisión profesional de estilo académico',
    'deteccion_plagio': 'Detección básica de posible plagio',
    'preparacion_presentacion': 'Preparación para presentación oral'
}