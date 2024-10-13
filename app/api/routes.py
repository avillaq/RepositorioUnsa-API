from flask import jsonify, request
from app.api.models import Documento, Coleccion
from app.api import bp
from app.extensions import db, limiter, cache

@bp.route('/documentos', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_documentos():
    titulo = request.args.get('titulo')
    fecha = request.args.get('fecha')
    uri = request.args.get('uri')

    # Parametros para ordenar
    sort_by = request.args.get('sort_by', 'titulo')  # Por defecto es el título
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente

    # Paginación
    page = request.args.get('page', 1, type=int)  # Página actual. 1 por defecto
    per_page = request.args.get('per_page', 10, type=int)  # Resultados por página. 10 por defecto

    query = Documento.query

    # Filtrar la consulta
    if titulo:
        query = query.filter(Documento.titulo.like(f'%{titulo}%'))
    if fecha:
        query = query.filter_by(fecha=fecha)
    if uri:
        query = query.filter_by(uri=uri)

    # Ordenar la consulta
    if sort_by in ['titulo', 'fecha', 'uri']:
        if order == 'desc':
            query = query.order_by(db.desc(getattr(Documento, sort_by)))
        else:
            query = query.order_by(getattr(Documento, sort_by))

    # Aplicar paginación
    documentos_paginados = query.paginate(page=page, per_page=per_page)

    resultado = {
        'page': documentos_paginados.page,
        'total_pages': documentos_paginados.pages,
        'total_items': documentos_paginados.total,
        'items': [documento.format() for documento in documentos_paginados.items]
    }
    return jsonify(resultado)

@bp.route('/colecciones', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_colecciones():
    nombre_coleccion = request.args.get('nombre_coleccion')

    # Parametros para ordenar
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente

    # Paginación
    page = request.args.get('page', 1, type=int)  # Página actual. 1 por defecto
    per_page = request.args.get('per_page', 10, type=int)  # Resultados por página. 10 por defecto

    query = Coleccion.query

    # Filtrar la consulta
    if nombre_coleccion:
        query = query.filter(Coleccion.nombre_coleccion.like(f'%{nombre_coleccion}%'))

    # Ordenar la consulta
    if order == 'desc':
        query = query.order_by(db.desc(Coleccion.nombre_coleccion))
    else:
        query = query.order_by(Coleccion.nombre_coleccion)

    # Aplicar paginación
    colecciones_paginados = query.paginate(page=page, per_page=per_page)

    resultado = {
        'page': colecciones_paginados.page,
        'total_pages': colecciones_paginados.pages,
        'total_items': colecciones_paginados.total,
        'items': [coleccion.format() for coleccion in colecciones_paginados.items]
    }
    return jsonify(resultado)

@bp.errorhandler(429)
def ratelimit_error(e):
    return jsonify(error="Rate limit exceeded", message=str(e.description)), 429

@bp.route('/')
def index():
    return jsonify(message="Welcome to the API")