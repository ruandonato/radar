# coding:utf-8
from __future__ import unicode_literals
from modelagem.models import Proposicao, CasaLegislativa
import urllib2
import xml.etree.ElementTree as etree
import logging

logger = logging.getLogger("radar")


def get_materia_xml(proposicao):
    url = "http://legis.senado.gov.br/dadosabertos/materia/%s/%s/%s" % \
        (proposicao.sigla, proposicao.numero, proposicao.ano)
    try:
        request = urllib2.Request(url)
        materia_xml = urllib2.urlopen(request).read()
    except urllib2.URLError, error:
        logger.error("urllib2.URLError: %s" % error)
        raise ValueError(
            'materia_xml não encontrada para %s %s/%s' %
            (proposicao.sigla, proposicao.numero, proposicao.ano))
    try:
        tree = etree.fromstring(materia_xml)
    except etree.ParseError, error:
        logger.error("etree.ParseError: %s" % error)
        raise ValueError(
            'materia_xml não encontrada para %s %s/%s' %
            (proposicao.sigla, proposicao.numero, proposicao.ano))
    return tree


def inserirIndex(proposicao):
    materia_xml = get_materia_xml(proposicao)
    ementa = materia_xml.find(
        "Materia").find("DadosBasicosMateria").find("EmentaMateria")
    if ementa is not None:
        proposicao.descricao = ementa.text
    index = materia_xml.find(
        "Materia").find("DadosBasicosMateria").find("IndexacaoMateria")
    if index is not None:
        proposicao.indexacao = index.text
    proposicao.save()


def indexar_proposicoes():
    senado = CasaLegislativa.objects.get(nome_curto="sen")
    proposicoes = Proposicao.objects.filter(casa_legislativa=senado,
                                            indexacao__isnull=True,
                                            ementa__isnull=True)
    for proposicao in proposicoes:
        inserirIndex(proposicao)


def main():
    indexar_proposicoes()
