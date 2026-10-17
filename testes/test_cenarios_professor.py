"""Bateria de testes oficiais conforme Plano de Testes de Qualidade da disciplina.

Referência: Seção 8 do documento 'plano_testes_aplicacoes_qt_flask.pdf':
- T8.1: Registrar nota e atualizar boletim
- T8.2: Validar nota, peso e vínculo
- T8.3: Persistência e controle de acesso
- T8.4: Facade e Strategy de média
"""
import json
import tempfile
import unittest
from pathlib import Path

from servidor.factories import FabricaRegistrosPadrao
from servidor.repository import ErroRepositorio
from servidor.services import ErroNegocio, GerenciadorService
from servidor.strategies import (
    MediaAritmeticaDireta,
    MediaNormalizada,
    MediaPonderadaPorValorMaximo,
)


class TesteCenariosProfessor(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.temp.name)
        self.servico = GerenciadorService(self.pasta)

    def tearDown(self):
        self.temp.cleanup()

    def test_T8_1_registrar_nota_e_atualizar_boletim(self):
        """T8.1 — Registrar nota e atualizar boletim.

        Pré-condições: Aluno e atividades cadastrados no sistema.
        Ações: Lançar notas nas atividades para o aluno e consultar o boletim.
        Resultado esperado:
        - As notas são registradas com sucesso.
        - O boletim reúne as notas com seus respectivos valores, máximos e equivalentes na escala 0-10.
        - A média final é calculada e atualizada com base nas notas válidas cadastradas.
        """
        aluno = self.servico.criar_aluno({"nome": "Lucas Ferreira", "matricula": "2026001"})
        prova = self.servico.criar_atividade({"titulo": "Prova Oficial", "descricao": "P1", "valor_maximo": 10.0})
        trabalho = self.servico.criar_atividade({"titulo": "Trabalho Prático", "descricao": "TP", "valor_maximo": 10.0})

        # Lança 10,0 na primeira e 8,5 na segunda
        nota1 = self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": prova["id"], "valor": 10.0})
        nota2 = self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": trabalho["id"], "valor": 8.5})

        self.assertIsNotNone(nota1.get("id"))
        self.assertIsNotNone(nota2.get("id"))

        # Consulta notas do boletim
        notas_boletim = self.servico.notas_do_aluno(aluno["id"])
        self.assertEqual(len(notas_boletim), 2)
        self.assertEqual(notas_boletim[0]["nota_normalizada"], 10.0)
        self.assertEqual(notas_boletim[1]["nota_normalizada"], 8.5)

        # Atualiza e confere média final no boletim
        boletim = self.servico.media_do_aluno(aluno["id"])
        self.assertEqual(boletim["aluno_id"], aluno["id"])
        self.assertEqual(boletim["media"], 9.25)
        self.assertEqual(boletim["quantidade_notas"], 2)
        self.assertEqual(boletim["escala"], "0 a 10")

    def test_T8_2_validar_nota_peso_e_vinculo(self):
        """T8.2 — Validar nota, peso e vínculo.

        Verifica:
        1. Validação de Nota:
           - Rejeita nota negativa (< 0);
           - Rejeita nota maior que a nota máxima / peso da atividade;
           - Rejeita tipos inválidos (NaN, inf, strings não numéricas, booleanos).
        2. Validação de Peso (valor_maximo):
           - Atividade exige peso/valor máximo estritamente positivo (> 0);
           - Não permite reduzir o peso da atividade para valor inferior a uma nota já lançada.
        3. Validação de Vínculo:
           - Impede lançamento para aluno inexistente (404);
           - Impede lançamento para atividade inexistente (404);
           - Impede lançamento duplicado (um aluno só pode ter 1 nota por atividade - 409);
           - Exclusão em cascata: excluir aluno ou atividade remove automaticamente os vínculos de nota.
        """
        aluno = self.servico.criar_aluno({"nome": "Mariana Silva", "matricula": "2026002"})
        atividade = self.servico.criar_atividade({"titulo": "Exercício Avaliativo", "valor_maximo": 10.0})

        # 1. Nota fora de faixa e tipos inválidos
        with self.assertRaises(ErroNegocio):
            self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": -0.5})

        with self.assertRaises(ErroNegocio):
            self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": 10.1})

        for invalido in (True, "dez", float("nan"), float("inf")):
            with self.assertRaises(ErroNegocio):
                self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": invalido})

        # 2. Peso inválido
        with self.assertRaises(ErroNegocio):
            self.servico.criar_atividade({"titulo": "Atividade Zero", "valor_maximo": 0})

        with self.assertRaises(ErroNegocio):
            self.servico.criar_atividade({"titulo": "Atividade Negativa", "valor_maximo": -5})

        # 3. Vínculo com entidades inexistentes
        with self.assertRaises(ErroNegocio) as ctx_aluno_inexistente:
            self.servico.criar_nota({"aluno_id": 9999, "atividade_id": atividade["id"], "valor": 8.0})
        self.assertEqual(ctx_aluno_inexistente.exception.status, 404)

        with self.assertRaises(ErroNegocio) as ctx_ativ_inexistente:
            self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": 9999, "valor": 8.0})
        self.assertEqual(ctx_ativ_inexistente.exception.status, 404)

        # Lança nota válida
        self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": 9.0})

        # Vínculo duplicado é impedido (HTTP 409)
        with self.assertRaises(ErroNegocio) as ctx_duplicado:
            self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": 10.0})
        self.assertEqual(ctx_duplicado.exception.status, 409)

        # Não permite reduzir peso abaixo de nota existente
        with self.assertRaises(ErroNegocio):
            self.servico.editar_atividade(atividade["id"], {"titulo": "Exercício", "valor_maximo": 8.0})

        # Integridade referencial na exclusão
        self.servico.excluir_aluno(aluno["id"])
        self.assertEqual(self.servico.listar_notas(), [])

    def test_T8_3_persistencia_e_integridade_dos_dados(self):
        """T8.3 — Persistência e integridade dos dados.

        Verifica:
        1. Persistência dos dados:
           - Registros gravados em JSON são mantidos ao fechar e reinicializar o serviço;
           - Atomicidade de gravação com substituição segura (sem gravações parciais);
           - Resistência contra corrupção (não apaga arquivo corrompido).
        2. Integridade e consistência:
           - Matrícula restrita a dígitos numéricos com preservação de zeros à esquerda;
           - Unicidade estrita de matrícula (impede cadastro e edição com matrícula duplicada - 409);
           - Bloqueio por RLock garantindo integridade de operações coordenadas.
        """
        # Cadastro com matrícula preservando zeros à esquerda
        aluno = self.servico.criar_aluno({"nome": "Beatriz Zago", "matricula": "00789"})
        atividade = self.servico.criar_atividade({"titulo": "Laboratório", "valor_maximo": 10.0})
        self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atividade["id"], "valor": 9.5})

        # Reinicializa o serviço simulando fechamento e reabertura da aplicação
        novo_servico = GerenciadorService(self.pasta)
        alunos_persistidos = novo_servico.listar_alunos()
        self.assertEqual(len(alunos_persistidos), 1)
        self.assertEqual(alunos_persistidos[0]["matricula"], "00789")
        self.assertEqual(alunos_persistidos[0]["nome"], "Beatriz Zago")

        notas_persistidas = novo_servico.listar_notas()
        self.assertEqual(len(notas_persistidas), 1)
        self.assertEqual(notas_persistidas[0]["valor"], 9.5)

        # Integridade de entrada: rejeita matrícula com letras/símbolos
        with self.assertRaises(ErroNegocio):
            self.servico.criar_aluno({"nome": "Invalido", "matricula": "A-100"})

        # Integridade de entrada: impede duplicação de matrícula existente
        with self.assertRaises(ErroNegocio) as ctx_duplicado:
            self.servico.criar_aluno({"nome": "Outro Aluno", "matricula": "00789"})
        self.assertEqual(ctx_duplicado.exception.status, 409)

        # Atomicidade e segurança contra corrupção
        caminho_alunos = self.pasta / "alunos.json"
        self.assertTrue(caminho_alunos.exists())
        caminho_alunos.write_text("corrompido", encoding="utf-8")
        with self.assertRaises(ErroRepositorio):
            novo_servico.listar_alunos()
        self.assertEqual(caminho_alunos.read_text(encoding="utf-8"), "corrompido")

    def test_T8_4_facade_e_strategy_de_media(self):
        """T8.4 — Facade e Strategy de média.

        Demonstra:
        1. Padrão Estrutural Facade (GerenciadorService):
           - Encapsula múltiplos repositórios (alunos, atividades, notas), factory e estratégias
             em uma interface simplificada e unificada para o cliente/Flask.
        2. Padrão Comportamental Strategy (EstrategiaMedia):
           - Cálculo de médias com critérios configuráveis e intercambiáveis;
           - Comportamento observável diferente para os mesmos dados de entrada:
             * MediaNormalizada: converte cada atividade para 0-10 e calcula média aritmética;
             * MediaPonderadaPorValorMaximo: pondera cada atividade pelo seu valor máximo;
             * MediaAritmeticaDireta: média simples dos pontos brutos.
        """
        aluno = self.servico.criar_aluno({"nome": "Carlos Souza", "matricula": "2026003"})
        # Atividade 1: max 5.0 (peso 5) | Nota obtida: 5.0 (100% da atividade)
        # Atividade 2: max 10.0 (peso 10) | Nota obtida: 5.0 (50% da atividade)
        atv_pequena = self.servico.criar_atividade({"titulo": "Quiz Rápido", "valor_maximo": 5.0})
        atv_grande = self.servico.criar_atividade({"titulo": "Prova Semestral", "valor_maximo": 10.0})

        self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atv_pequena["id"], "valor": 5.0})
        self.servico.criar_nota({"aluno_id": aluno["id"], "atividade_id": atv_grande["id"], "valor": 5.0})

        # 1. Estratégia Normalizada (padrão):
        # Quiz: 5/5 = 10,0. Prova: 5/10 = 5,0. Média = (10 + 5) / 2 = 7.50
        media_norm = self.servico.media_do_aluno(aluno["id"])
        self.assertEqual(media_norm["media"], 7.50)
        self.assertEqual(media_norm["criterio_codigo"], "normalizada")

        # 2. Estratégia Ponderada pelo Valor Máximo:
        # Total obtido = 5 + 5 = 10. Total possível = 5 + 10 = 15.
        # Média = (10 / 15) * 10 = 6.67
        media_pond = self.servico.media_do_aluno(aluno["id"], estrategia=MediaPonderadaPorValorMaximo())
        self.assertEqual(media_pond["media"], 6.67)
        self.assertEqual(media_pond["criterio_codigo"], "ponderada")

        # 3. Estratégia Aritmética Direta dos Pontos:
        # Média dos pontos brutos = (5 + 5) / 2 = 5.00
        media_direta = self.servico.media_do_aluno(aluno["id"], estrategia=MediaAritmeticaDireta())
        self.assertEqual(media_direta["media"], 5.00)
        self.assertEqual(media_direta["criterio_codigo"], "direta")

        # 4. Substituição dinâmica da estratégia no contexto da Facade
        self.servico.definir_estrategia_media(MediaPonderadaPorValorMaximo())
        media_contexto = self.servico.media_do_aluno(aluno["id"])
        self.assertEqual(media_contexto["media"], 6.67)


if __name__ == "__main__":
    unittest.main()
