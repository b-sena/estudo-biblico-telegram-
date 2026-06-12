import os
import time
import requests
from datetime import datetime, timedelta, timezone

# ============================================================
# CONFIGURAÇÃO
# ============================================================
ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY")

EVOLUTION_URL      = os.getenv("EVOLUTION_URL")
EVOLUTION_APIKEY   = os.getenv("EVOLUTION_APIKEY")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE")

PHONE_1  = os.getenv("EVOLUTION_PHONE_1")
PHONE_2  = os.getenv("EVOLUTION_PHONE_2")

# Para ativar o grupo, remova o comentário abaixo e adicione o secret no GitHub:
# GROUP_ID = os.getenv("EVOLUTION_GROUP")  # 120363040976590973@g.us

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY não definida")

# ============================================================
# 365 TEMAS BÍBLICOS — um por dia do ano, sem repetição
# Formato: ("Livro / Referência", "Tema", "Foco")
# ============================================================
TEMAS = [
    # JANEIRO
    ("Gênesis 1", "O começo de tudo", "criação, propósito e identidade em Deus"),
    ("Gênesis 2", "Feitos para relacionamento", "comunhão, completude e cuidado mútuo"),
    ("Gênesis 3", "A queda e a promessa", "pecado, consequência e a primeira promessa de redenção"),
    ("Gênesis 12", "A chamada de Abraão", "fé, obediência e deixar o conhecido por Deus"),
    ("Gênesis 15", "A aliança com Abraão", "promessa de Deus, fé contada como justiça"),
    ("Gênesis 22", "A prova de Abraão", "obediência radical, confiança e provisão divina"),
    ("Gênesis 37", "A história de José começa", "sonhos, rejeição e o plano soberano de Deus"),
    ("Gênesis 50", "O perdão de José", "reconciliação, perdão e propósito no sofrimento"),
    ("Êxodo 3", "A sarça ardente", "o chamado de Moisés, santidade de Deus e missão"),
    ("Êxodo 12", "A Páscoa", "libertação, sangue do cordeiro e redenção"),
    ("Êxodo 14", "A travessia do Mar Vermelho", "impossível para o homem, possível para Deus"),
    ("Êxodo 20", "Os Dez Mandamentos", "lei de Deus, amor e ordenança para a vida"),
    ("Êxodo 33", "A presença de Deus", "buscar a face de Deus acima de tudo"),
    ("Levítico 19", "Santos como Deus é santo", "santidade prática, amor ao próximo"),
    ("Números 14", "A incredulidade no deserto", "fé versus medo, consequências da desconfiança"),
    ("Deuteronômio 6", "Amar a Deus com tudo", "o grande mandamento, ensinar a próxima geração"),
    ("Deuteronômio 8", "Não esqueça de onde viemos", "gratidão, memória, humildade diante de Deus"),
    ("Deuteronômio 31", "Sede fortes e corajosos", "coragem, presença de Deus e transição de liderança"),
    ("Josué 1", "Seja forte e corajoso", "encorajamento, presença de Deus e nova temporada"),
    ("Josué 24", "Quanto a mim e à minha casa", "compromisso, escolha deliberada de servir a Deus"),
    ("Juízes 6", "O chamado de Gideão", "Deus chama os improvistas, fraqueza e poder divino"),
    ("Rute 1", "Lealdade de Rute", "fidelidade, amor que fica, compromisso além das circunstâncias"),
    ("Rute 4", "A redenção de Rute", "redentor, restauração e providência de Deus"),
    ("1 Samuel 3", "O chamado de Samuel", "ouvir a voz de Deus, disponibilidade e obediência"),
    ("1 Samuel 16", "Deus vê o coração", "aparência versus caráter, escolha de Davi"),
    ("1 Samuel 17", "Davi e Golias", "coragem, fé e enfrentar gigantes com Deus"),
    ("2 Samuel 7", "A aliança com Davi", "promessa, descendência e trono eterno"),
    ("2 Samuel 11–12", "Davi, Bate-Seba e Natã", "pecado oculto, arrependimento genuíno e restauração"),
    ("1 Reis 3", "A sabedoria de Salomão", "pedir sabedoria, discernimento acima de riquezas"),
    ("1 Reis 18", "Elias no monte Carmelo", "fé solitária, poder de Deus e o falso versus o real"),
    ("1 Reis 19", "Elias no deserto", "esgotamento, cuidado de Deus e voz mansa e delicada"),
    # FEVEREIRO
    ("2 Reis 5", "A cura de Naamã", "humildade, obediência simples e graça inesperada"),
    ("2 Reis 22", "O livro da lei encontrado", "renovação espiritual, arrependimento e volta a Deus"),
    ("1 Crônicas 16", "Louvor e gratidão", "adoração, memória das obras de Deus e proclamação"),
    ("2 Crônicas 7", "Se o meu povo se humilhar", "avivamento, humildade, oração e restauração"),
    ("2 Crônicas 20", "Josafá diante da batalha", "orar antes de agir, louvor como estratégia de guerra"),
    ("Esdras 3", "O altar reconstruído", "prioridade da adoração na reconstrução espiritual"),
    ("Neemias 1", "Neemias ora pelo povo", "intercessão, identificação com o pecado coletivo"),
    ("Neemias 4", "Construir com uma mão e lutar com a outra", "perseverança diante da oposição"),
    ("Ester 4", "Para um momento como este", "propósito providencial, coragem e missão"),
    ("Jó 1", "Jó é posto à prova", "soberania de Deus, fé sem garantias visíveis"),
    ("Jó 19", "Eu sei que o meu Redentor vive", "esperança inabalável no meio da dor extrema"),
    ("Jó 38", "Onde estavas tu?", "grandeza de Deus, humildade humana diante do mistério"),
    ("Jó 42", "A restauração de Jó", "rendição, oração pelos inimigos e restauração plena"),
    ("Salmos 1", "O homem bem-aventurado", "meditar na Palavra, escolha do caminho certo"),
    ("Salmos 8", "A grandeza de Deus e o valor do homem", "maravilha da criação e dignidade humana"),
    ("Salmos 16", "Deus é a minha herança", "satisfação em Deus, segurança e alegria plena"),
    ("Salmos 19", "Os céus proclamam", "revelação de Deus na criação e na Palavra"),
    ("Salmos 22", "O clamor do abandono", "sofrimento de Cristo prefigurado, clamor e confiança"),
    ("Salmos 23", "O Senhor é meu pastor", "provisão, proteção e acompanhamento divino"),
    ("Salmos 27", "O Senhor é a minha luz", "confiança sem medo, buscar a face de Deus"),
    ("Salmos 32", "A bênção do perdão", "confissão, arrependimento e alegria restaurada"),
    ("Salmos 34", "Provai e vede", "experiência pessoal com Deus, louvor no sofrimento"),
    ("Salmos 37", "Descansa no Senhor", "confiança no tempo de Deus, não invejar o ímpio"),
    ("Salmos 42", "Como o cervo brama", "sede de Deus, depressão espiritual e esperança"),
    ("Salmos 46", "Deus é o nosso refúgio", "certeza em meio ao caos, Deus como fortaleza"),
    ("Salmos 51", "O salmo do arrependimento", "graça, restauração e coração contrito"),
    ("Salmos 62", "Em Deus somente", "descanso na soberania, esperança como rocha"),
    ("Salmos 63", "Te busco desde a madrugada", "desejo profundo por Deus, intimidade na adoração"),
    # MARÇO
    ("Salmos 71", "Esperança na velhice", "fidelidade de Deus ao longo da vida, louvor contínuo"),
    ("Salmos 73", "A inveja do próspero ímpio", "perspectiva eterna, valor da presença de Deus"),
    ("Salmos 84", "Como são amáveis os teus tabernáculos", "amor pela presença de Deus, um dia no templo"),
    ("Salmos 86", "Inclina o teu ouvido, Senhor", "dependência total de Deus, oração de necessidade"),
    ("Salmos 90", "De geração em geração", "efemeridade da vida, eternidade de Deus, sabedoria"),
    ("Salmos 91", "Debaixo da sombra do Altíssimo", "proteção divina, confiança nos perigos"),
    ("Salmos 100", "Entrai com louvor", "adoração coletiva, gratidão e pertencimento ao povo de Deus"),
    ("Salmos 103", "Bendize a Deus, ó minha alma", "misericórdia, perdão e amor eterno de Deus"),
    ("Salmos 107", "Os remidos do Senhor digam", "libertação, testemunho e gratidão"),
    ("Salmos 112", "O homem temente a Deus", "caráter do justo, benção e influência"),
    ("Salmos 119:1–16", "A Palavra como luz", "amor pela Escritura, meditação e obediência"),
    ("Salmos 121", "O meu socorro vem do Senhor", "proteção, guardião de Israel e do crente"),
    ("Salmos 126", "Quando o Senhor restaurou", "avivamento, choro e colheita de alegria"),
    ("Salmos 130", "Das profundezas clamo", "perdão, espera e esperança em Deus"),
    ("Salmos 139", "Senhor, tu me sondas", "onisciência, criação e conhecimento íntimo de Deus"),
    ("Salmos 145", "Louvarei o teu nome para sempre", "grandeza, bondade e reino eterno de Deus"),
    ("Provérbios 1", "O começo da sabedoria", "temor do Senhor, sabedoria como base da vida"),
    ("Provérbios 3", "Confia no Senhor", "dependência de Deus, honrá-lo com as primícias"),
    ("Provérbios 4", "Guarda o teu coração", "caráter, fonte da vida e caminhos de sabedoria"),
    ("Provérbios 11", "A bondade e a integridade", "generosidade, honestidade e seus frutos"),
    ("Provérbios 15", "A resposta mansa", "palavras que curam ou destroem, comunicação sábia"),
    ("Provérbios 16", "O coração do homem planeja", "soberania de Deus e planos humanos"),
    ("Provérbios 31", "A mulher virtuosa", "caráter, diligência, família e temor ao Senhor"),
    ("Eclesiastes 1–2", "Vaidade das vaidades", "sentido da vida fora de Deus, busca vazia"),
    ("Eclesiastes 3", "Tudo tem o seu tempo", "propósito divino em cada estação da vida"),
    ("Eclesiastes 12", "Tema a Deus na juventude", "prioridade de Deus, conclusão da sabedoria"),
    ("Isaías 1", "O chamado ao arrependimento", "idolatria, injustiça social e apelo de Deus"),
    ("Isaías 6", "A visão de Isaías", "santidade de Deus, indignidade humana e missão"),
    ("Isaías 9", "Um filho nos é dado", "esperança messiânica, luz nas trevas"),
    ("Isaías 25", "Deus destrói a morte", "festa messiânica, vitória final e consolo"),
    ("Isaías 26", "Paz perfeita", "confiança como fundamento, paz que só Deus dá"),
    # ABRIL
    ("Isaías 40", "Os que esperam no Senhor", "conforto, grandeza de Deus e renovação de forças"),
    ("Isaías 41", "Não temas, pois estou contigo", "presença de Deus no medo, fortaleza e sustento"),
    ("Isaías 43", "Eu te redimi, és meu", "identidade em Deus, passagem pelas águas e fogo"),
    ("Isaías 46", "Eu carregarei você", "Deus carrega o seu povo, contraste com ídolos"),
    ("Isaías 49", "O servo da luz das nações", "missão, abandono aparente e restauração"),
    ("Isaías 53", "O servo sofredor", "substituto, dor carregada e justificação"),
    ("Isaías 55", "Vinde, comprai sem dinheiro", "graça gratuita, convite de Deus e retorno"),
    ("Isaías 58", "O jejum que Deus escolhe", "justiça social, verdadeiro culto e luz"),
    ("Isaías 61", "O Espírito do Senhor está sobre mim", "missão de Cristo, liberdade e restauração"),
    ("Isaías 65", "O novo céu e a nova terra", "esperança escatológica, renovação e alegria"),
    ("Jeremias 1", "O chamado de Jeremias", "vocação antes do nascimento, coragem e missão"),
    ("Jeremias 17", "Maldito o que confia no homem", "dependência de Deus versus confiança humana"),
    ("Jeremias 18", "O oleiro e o barro", "soberania de Deus, moldagem e propósito"),
    ("Jeremias 29", "A carta aos exilados", "prosperar no exílio, buscar o bem da cidade"),
    ("Jeremias 31", "A nova aliança", "lei no coração, conhecer a Deus, perdão completo"),
    ("Lamentações 3", "As misericórdias de Deus são novas", "dor, esperança renovada e fidelidade de Deus"),
    ("Ezequiel 36", "Coração novo, espírito novo", "transformação interior, obra do Espírito"),
    ("Ezequiel 37", "O vale dos ossos secos", "ressurreição, avivamento e poder do Espírito"),
    ("Daniel 1", "Propósito no coração", "fidelidade em cultura hostil, integridade e sabedoria"),
    ("Daniel 3", "A fornalha ardente", "recusa à idolatria, Deus que livra e presença no fogo"),
    ("Daniel 6", "Daniel na cova dos leões", "fidelidade na perseguição, oração constante"),
    ("Oséias 2", "Eu a atrairei", "amor de Deus pelo povo infiel, restauração do casamento"),
    ("Oséias 11", "Quando Israel era criança", "amor paternal de Deus, graça que persevera"),
    ("Joel 2", "Derramarei do meu Espírito", "arrependimento, restauração e Pentecostes"),
    ("Amós 5", "Buscai a mim e vivereis", "chamado à justiça, adoração e busca de Deus"),
    ("Jonas 1–2", "A fuga e o ventre do peixe", "desobediência, consequência e misericórdia de Deus"),
    ("Jonas 4", "A misericórdia de Deus", "graça para os inimigos, coração de Deus pelos perdidos"),
    ("Miquéias 6", "O que o Senhor requer", "justiça, misericórdia e humildade"),
    ("Habacuque 3", "Ainda me alegrarei", "fé quando tudo falha, alegria no Deus da salvação"),
    ("Sofonias 3", "O Senhor se alegra sobre ti", "amor de Deus que canta, restauração e alegria"),
    # MAIO
    ("Ageu 1", "Considerai o vosso caminho", "prioridades, buscar primeiro o reino de Deus"),
    ("Zacarias 4", "Não por força nem por poder", "dependência do Espírito, pequenos começos"),
    ("Malaquias 3", "Voltai-vos a mim", "fidelidade nas dádivas, janelas do céu, arrependimento"),
    ("Mateus 5", "O sermão da montanha — as bem-aventuranças", "valores do reino, felicidade verdadeira"),
    ("Mateus 6", "Não vos preocupeis", "confiança em Deus, oração e buscar o reino"),
    ("Mateus 7", "Pedí e recebereis", "persistência em oração, o pai que dá bons dons"),
    ("Mateus 11", "Vinde a mim os cansados", "descanso em Cristo, jugo leve e aprendizado"),
    ("Mateus 13", "O semeador", "tipos de solo do coração, recepção da Palavra"),
    ("Mateus 14", "Pedro anda sobre as águas", "fé, olhar para Cristo, não para a tempestade"),
    ("Mateus 16", "Quem dizeis que eu sou?", "identidade de Cristo, revelação e fé pessoal"),
    ("Mateus 18", "A ovelha perdida", "amor de Deus pelo perdido, restauração e comunidade"),
    ("Mateus 25", "As dez virgens", "vigilância espiritual, prontidão para o retorno de Cristo"),
    ("Mateus 28", "A grande comissão", "missão universal, autoridade de Cristo e presença"),
    ("Marcos 1", "O começo do evangelho", "urgência, arrependimento e chamado dos primeiros discípulos"),
    ("Marcos 4", "A tempestade acalmada", "fé no barco, Cristo que acalma o que nos aterroriza"),
    ("Marcos 10", "Quem quiser ser grande", "serviço, humildade e o modelo de Cristo"),
    ("Lucas 1", "O cântico de Maria", "magnificat, reverência, misericórdia e grandeza de Deus"),
    ("Lucas 2", "O nascimento de Jesus", "encarnação, glória revelada e o Salvador prometido"),
    ("Lucas 10", "Marta e Maria", "prioridade da presença de Cristo sobre a agitação"),
    ("Lucas 15", "O filho pródigo", "amor do pai, arrependimento, celebração e graça"),
    ("Lucas 18", "A viúva persistente", "perseverança em oração, justiça de Deus e fé"),
    ("Lucas 19", "Zaqueu", "salvação que transforma, busca de Cristo pelos perdidos"),
    ("Lucas 22–23", "A última ceia e a cruz", "sacrifício, entrega e amor extremo de Cristo"),
    ("Lucas 24", "A ressurreição", "vitória sobre a morte, esperança e missão renovada"),
    ("João 1", "No princípio era o Verbo", "divindade de Cristo, encarnação e graça sobre graça"),
    ("João 3", "Deus amou o mundo", "salvação por graça, novo nascimento e amor de Deus"),
    ("João 4", "A mulher samaritana", "água viva, adoração em espírito e verdade"),
    ("João 6", "Eu sou o pão da vida", "dependência de Cristo, satisfação espiritual e fé"),
    ("João 8", "Eu sou a luz do mundo", "liberdade da verdade, escravidão ao pecado e graça"),
    ("João 10", "Eu sou o bom pastor", "conhecimento mútuo, vida abundante e proteção"),
    ("João 11", "A ressurreição de Lázaro", "Cristo sobre a morte, esperança no luto, glória de Deus"),
    # JUNHO
    ("João 13", "O lava-pés", "serviço humilde, amor prático e exemplo de Cristo"),
    ("João 14", "Não se turbe o vosso coração", "paz de Cristo, morada eterna e o Consolador"),
    ("João 15", "Permaneçam em mim", "videira e ramos, fruto e amor que permanece"),
    ("João 17", "A oração sacerdotal", "unidade, proteção e glorificação"),
    ("João 20", "Maria no sepulcro vazio", "ressurreição, reconhecimento de Cristo e missão"),
    ("João 21", "Amas-me?", "restauração de Pedro, missão renovada e amor a Cristo"),
    ("Atos 1", "Esperai a promessa do Pai", "Espírito Santo, testemunhas e ascensão de Cristo"),
    ("Atos 2", "O dia de Pentecostes", "derramamento do Espírito, poder e nascimento da Igreja"),
    ("Atos 4", "Oração de ousadia", "perseguição, oração coletiva e coragem apostólica"),
    ("Atos 9", "A conversão de Paulo", "graça transformadora, identidade renovada e missão"),
    ("Atos 16", "Paulo e Silas na prisão", "louvor no sofrimento, libertação e testemunho"),
    ("Romanos 1", "Não me envergonho do evangelho", "poder do evangelho, fé e justiça de Deus"),
    ("Romanos 3", "Todos pecaram", "necessidade universal de salvação e graça justificadora"),
    ("Romanos 5", "Paz com Deus pela fé", "justificação, paz, esperança e amor de Deus na cruz"),
    ("Romanos 6", "Mortos para o pecado", "identidade em Cristo, liberdade e vida nova"),
    ("Romanos 7", "A luta interior", "tensão espiritual, fraqueza humana e dependência de Cristo"),
    ("Romanos 8", "Nenhuma condenação", "vida no Espírito, filhos de Deus e mais que vencedores"),
    ("Romanos 10", "Confessa com a boca", "salvação acessível, fé e necessidade de proclamação"),
    ("Romanos 12", "Sacrifício vivo", "transformação pela renovação, serviço e amor prático"),
    ("Romanos 15", "Esperança pelo poder do Espírito", "encorajamento mútuo, missão e paz de Deus"),
    ("1 Coríntios 1", "A loucura da cruz", "sabedoria de Deus versus sabedoria humana"),
    ("1 Coríntios 3", "Plantadores e regadores", "colaboração, fundação em Cristo e obra de Deus"),
    ("1 Coríntios 9", "Tudo faço por causa do evangelho", "adaptação cultural, serviço e missão"),
    ("1 Coríntios 10", "Não tenteis ao Senhor", "advertências do deserto, fidelidade e tentações"),
    ("1 Coríntios 12", "Os dons do Espírito", "variedade de dons, um Espírito e corpo de Cristo"),
    ("1 Coríntios 13", "O hino do amor", "amor como maior dom, paciência e perseverança"),
    ("1 Coríntios 15", "A ressurreição dos mortos", "esperança futura, vitória sobre a morte e missão"),
    ("2 Coríntios 1", "O Deus de toda consolação", "conforto no sofrimento e consolar os outros"),
    ("2 Coríntios 3", "A glória do novo ministério", "transformação à imagem de Cristo, liberdade"),
    ("2 Coríntios 4", "Tesouros em vasos de barro", "fraqueza que revela o poder de Deus"),
    ("2 Coríntios 5", "Nova criação em Cristo", "reconciliação, identidade nova e embaixadores"),
    # JULHO
    ("2 Coríntios 9", "Deus ama quem dá com alegria", "generosidade, semeadura e graça abundante"),
    ("2 Coríntios 10", "Armas poderosas em Deus", "guerra espiritual, pensamentos e autoridade"),
    ("2 Coríntios 12", "O espinho na carne", "fraqueza, graça suficiente e poder em Cristo"),
    ("Gálatas 2", "Crucificado com Cristo", "identidade em Cristo, vida por fé e graça"),
    ("Gálatas 3", "Justificados pela fé", "lei versus fé, herança de Abraão e filhos de Deus"),
    ("Gálatas 5", "O fruto do Espírito", "liberdade verdadeira, andar no Espírito e caráter"),
    ("Gálatas 6", "Cada um levará sua carga", "restauração com mansidão, colheita e generosidade"),
    ("Efésios 1", "Abençoados com toda bênção espiritual", "eleição, adoção e herança em Cristo"),
    ("Efésios 2", "Salvos pela graça mediante a fé", "morte espiritual, ressurreição e unidade"),
    ("Efésios 3", "O mistério revelado em Cristo", "riquezas insondáveis, amor que excede o conhecimento"),
    ("Efésios 4", "A unidade do Espírito", "maturidade, dons e falar a verdade em amor"),
    ("Efésios 5", "Sede imitadores de Deus", "amor, luz, gratidão e relacionamentos transformados"),
    ("Efésios 6", "A armadura de Deus", "guerra espiritual, oração e firmeza em Cristo"),
    ("Filipenses 1", "Para mim o viver é Cristo", "propósito, prisão que avança o evangelho e ousadia"),
    ("Filipenses 2", "Nada por egoísmo", "humildade de Cristo, unidade e brilhar como estrelas"),
    ("Filipenses 3", "Esqueço o que ficou para trás", "identidade em Cristo, maturidade e meta eterna"),
    ("Filipenses 4", "A paz que excede todo entendimento", "contentamento, gratidão e força em Cristo"),
    ("Colossenses 1", "Cristo, primogênito de toda criação", "supremacia de Cristo, reconciliação e missão"),
    ("Colossenses 2", "Arraigados e edificados em Cristo", "liberdade de tradições, plenitude em Cristo"),
    ("Colossenses 3", "Buscai as coisas do alto", "vida escondida em Cristo, renovação e relacionamentos"),
    ("1 Tessalonicenses 4", "Os que dormem em Cristo", "esperança na ressurreição, conforto na perda"),
    ("1 Tessalonicenses 5", "Orai sem cessar", "vigilância, gratidão e fidelidade até o fim"),
    ("2 Tessalonicenses 3", "Não vos canseis de fazer o bem", "perseverança, trabalho e encorajamento"),
    ("1 Timóteo 1", "Cristo veio para salvar os pecadores", "graça para o pior dos pecadores"),
    ("1 Timóteo 4", "Exercita-te para a piedade", "disciplina espiritual, exemplo e Palavra"),
    ("1 Timóteo 6", "A piedade com contentamento", "riqueza verdadeira, generosidade e propósito"),
    ("2 Timóteo 1", "Não nos deu espírito de covardia", "ousadia, amor, disciplina e identidade no evangelho"),
    ("2 Timóteo 2", "Soldado de Cristo Jesus", "perseverança, fidelidade e o trabalhador aprovado"),
    ("2 Timóteo 3", "Toda a Escritura é inspirada", "autoridade da Bíblia, instrução e perfeição"),
    ("2 Timóteo 4", "Combati o bom combate", "fidelidade até o fim, a coroa da justiça"),
    ("Tito 2", "A graça que nos ensina", "santificação pela graça, exemplo e vida sã"),
    # AGOSTO
    ("Filemom", "Mais que escravo, irmão amado", "perdão, reconciliação e igualdade em Cristo"),
    ("Hebreus 1", "Deus falou pelo seu Filho", "supremacia de Cristo, revelação final e perfeita"),
    ("Hebreus 4", "O descanso que resta ao povo de Deus", "entrar no descanso, graça e o sumo sacerdote"),
    ("Hebreus 10", "Não forsamos reunir-nos", "perseverança, comunidade e esperança na promessa"),
    ("Hebreus 11", "A nuvem de testemunhas", "fé que age, heróis da fé e esperança futura"),
    ("Hebreus 12", "Corramos com perseverança", "disciplina, olhar para Jesus e paz com todos"),
    ("Hebreus 13", "Jesus Cristo é o mesmo", "imutabilidade de Cristo, hospitalidade e contentamento"),
    ("Tiago 1", "A prova da fé gera perseverança", "tentação, sabedoria pedida e ouvintes da Palavra"),
    ("Tiago 2", "A fé sem obras é morta", "fé prática, cuidado com o próximo e justiça social"),
    ("Tiago 3", "O poder da língua", "palavras que abençoam ou destroem, sabedoria do alto"),
    ("Tiago 4", "Aproximai-vos de Deus", "humildade, resistir ao diabo e vida incerta"),
    ("Tiago 5", "A oração eficaz do justo", "intercessão, restauração e poder da oração"),
    ("1 Pedro 1", "Uma esperança viva", "ressurreição, herança imperecível e santidade"),
    ("1 Pedro 2", "Pedras vivas", "identidade do povo de Deus, sacerdócio real e testemunho"),
    ("1 Pedro 3", "Pronto para dar razão da esperança", "apologética com mansidão, sofrer pelo bem"),
    ("1 Pedro 4", "Usando os dons para servir", "mordomia dos dons, amor e glória a Deus"),
    ("1 Pedro 5", "Humilhai-vos sob a poderosa mão de Deus", "humildade, cuidado pastoral e firmeza"),
    ("2 Pedro 1", "Participantes da natureza divina", "virtudes cristãs, confirmação da vocação"),
    ("2 Pedro 3", "Deus não retarda a sua promessa", "paciência de Deus, arrependimento e novo mundo"),
    ("1 João 1", "Andemos na luz", "comunhão, confissão e purificação pelo sangue de Cristo"),
    ("1 João 2", "Não ameis o mundo", "amor ao Pai, guardar a Palavra e o Anticristo"),
    ("1 João 3", "Somos chamados filhos de Deus", "identidade, amor prático e confiança diante de Deus"),
    ("1 João 4", "Deus é amor", "amor como essência de Deus, amor que expulsa o medo"),
    ("1 João 5", "Esta é a vitória que vence o mundo", "fé, testemunho e vida eterna em Cristo"),
    ("2 João", "Andar na verdade e no amor", "equilíbrio entre verdade e amor na comunidade"),
    ("3 João", "Imita o que é bom", "hospitalidade, testemunho e imitar o bem"),
    ("Judas", "Contendais pela fé", "apostasia, graça que não é libertinagem e guardar a fé"),
    ("Apocalipse 1", "O Filho do Homem glorificado", "visão de Cristo ressurreto, soberano e eterno"),
    ("Apocalipse 2", "Cartas às igrejas — Éfeso", "primeiro amor, arrependimento e perseverança"),
    ("Apocalipse 3", "Cartas às igrejas — Laodiceia", "mornidão, disciplina de Cristo e abertura da porta"),
    ("Apocalipse 5", "O Cordeiro digno", "adoração celestial, vitória pelo sangue de Cristo"),
    # SETEMBRO
    ("Apocalipse 7", "Uma multidão inumerável", "salvação universal, adoração e vitória na tribulação"),
    ("Apocalipse 12", "A mulher e o dragão", "guerra espiritual, vitória pelo sangue e testemunho"),
    ("Apocalipse 19", "As bodas do Cordeiro", "retorno de Cristo, celebração eterna e vitória final"),
    ("Apocalipse 21", "Todas as coisas novas", "nova criação, fim do sofrimento e morada de Deus"),
    ("Apocalipse 22", "Vem, Senhor Jesus", "esperança escatológica, convite da graça e urgência"),
    ("Gênesis 28", "A escada de Jacó", "presença de Deus no lugar inesperado, promessa renovada"),
    ("Gênesis 32", "Jacó luta com Deus", "persistência em oração, transformação e bênção"),
    ("Êxodo 16", "O maná no deserto", "dependência diária de Deus, provisão fiel"),
    ("Êxodo 32", "O bezerro de ouro", "idolatria, intercessão de Moisés e misericórdia de Deus"),
    ("Números 6", "A bênção sacerdotal", "graça, paz e a face de Deus sobre nós"),
    ("Josué 3", "A travessia do Jordão", "passos de fé, milagres e entrada na promessa"),
    ("Josué 6", "A queda de Jericó", "obediência incomum, vitória de Deus e fé visível"),
    ("Juízes 16", "A queda de Sansão", "graça para os fracassados, força renovada em fraqueza"),
    ("1 Samuel 1", "A oração de Ana", "dor fértil, oração desesperada e fidelidade de Deus"),
    ("1 Samuel 7", "Até aqui nos ajudou o Senhor", "Ebenezer, memória das obras de Deus e gratidão"),
    ("2 Samuel 9", "A bondade de Davi a Mefibosete", "graça imerecida, restauração e mesa do rei"),
    ("1 Reis 8", "A dedicação do templo", "oração de Salomão, presença de Deus e perdão"),
    ("2 Reis 6", "Os que estão conosco são mais", "mundo espiritual, proteção e oração por visão"),
    ("Esdras 7", "A mão de Deus sobre Esdras", "capacitação divina, Palavra e missão"),
    ("Neemias 8", "A leitura da lei", "Palavra que traz alegria, ensino e celebração"),
    ("Ester 8–9", "A virada de Ester", "inversão, vitória e alegria restaurada"),
    ("Jó 5", "O homem nasce para a aflição", "consolo humano limitado, buscar a Deus"),
    ("Jó 23", "Onde encontrar a Deus?", "busca em meio ao silêncio, fé sem experiência sensível"),
    ("Salmos 2", "O Rei ungido de Deus", "soberania de Cristo, nações e esperança escatológica"),
    ("Salmos 11", "O Senhor está no seu santo templo", "refúgio em Deus quando os fundamentos tremem"),
    ("Salmos 18", "Eu te amo, Senhor, minha força", "libertação, gratidão e dependência de Deus"),
    ("Salmos 24", "Do Senhor é a terra", "santidade, buscar a face de Deus e rei da glória"),
    ("Salmos 25", "A ti, Senhor, elevo a minha alma", "confiança, ensino de Deus e perdão"),
    ("Salmos 28", "Força do meu povo", "clamor, fé ouvida e alegria que transborda"),
    ("Salmos 30", "O pranto dura uma noite", "virada de Deus, lamento em alegria"),
    ("Salmos 31", "Em tuas mãos entrego o meu espírito", "entrega total, socorro e confiança"),
    # OUTUBRO
    ("Salmos 33", "Cantai ao Senhor um cântico novo", "criação pela Palavra, planos de Deus e esperança"),
    ("Salmos 36", "Tua misericórdia, Senhor, chega aos céus", "bondade imensurável, luz e fonte de vida"),
    ("Salmos 40", "Ele me tirou do poço", "libertação, missão e nova canção"),
    ("Salmos 43", "Espera em Deus", "louvor no desânimo, esperança ativa"),
    ("Salmos 47", "Deus reina sobre as nações", "senhorio universal, adoração e triunfo"),
    ("Salmos 48", "Grande é o Senhor", "segurança na cidade de Deus, beleza e proteção"),
    ("Salmos 49", "A vaidade da riqueza", "riqueza que não salva, redenção e esperança eterna"),
    ("Salmos 50", "O Deus dos deuses fala", "sacrifício verdadeiro, gratidão e clamor a Deus"),
    ("Salmos 52", "A bondade de Deus é eterna", "contraste entre o mal e o confiante em Deus"),
    ("Salmos 55", "Lança sobre o Senhor o teu fardo", "traição, fardo e a segurança de confiar em Deus"),
    ("Salmos 56", "Em Deus confio sem temer", "medo, confiança e louvor antes da vitória"),
    ("Salmos 57", "Serei firme, ó meu coração", "determinação no sofrimento, glória de Deus"),
    ("Salmos 59", "Tu, Senhor, és minha força", "perseguição, refúgio e louvor pela manhã"),
    ("Salmos 60", "Deus falou no seu santuário", "derrota, restauração e vitória com Deus"),
    ("Salmos 61", "Conduz-me à rocha mais alta", "clamor do limite, refúgio e voto de louvor"),
    ("Salmos 64", "Deus defende o seu servo", "línguas malignas, obra de Deus e alegria do justo"),
    ("Salmos 65", "Louvores te são devidos", "criação, chuva e abundância de Deus"),
    ("Salmos 66", "Exultai a Deus, toda a terra", "maravilhas, prova e gratidão pela libertação"),
    ("Salmos 67", "Que os povos te louvem", "missão, bênção e testemunho às nações"),
    ("Salmos 68", "Deus se levanta", "vitória de Deus, cuidado com os solitários e louvores"),
    ("Salmos 69", "Salva-me, ó Deus", "clamor no sofrimento, identificação com Cristo"),
    ("Salmos 70", "Apressa-te em me ajudar", "urgência em oração, confiança e socorro de Deus"),
    ("Salmos 72", "O rei de justiça", "rei messiânico, justiça, paz e benção universal"),
    ("Salmos 74", "Até quando, ó Deus?", "clamor em tempos de abandono aparente e fé persistente"),
    ("Salmos 75", "Nós te louvamos, ó Deus", "soberania de Deus no julgamento e na exaltação"),
    ("Salmos 76", "Deus é temido entre os sábios", "poder de Deus, paz que ele estabelece"),
    ("Salmos 77", "Lembrarei as obras do Senhor", "crise espiritual, memória e fé renovada"),
    ("Salmos 78", "O que ouvimos e conhecemos", "ensinar às gerações, fidelidade e infidelidade"),
    ("Salmos 79", "Ó Deus, as nações invadiram", "clamor coletivo, glória de Deus e restauração"),
    ("Salmos 80", "Restaura-nos, ó Deus", "clamor da vinha, avivamento e face de Deus"),
    ("Salmos 81", "Cantai com alegria a Deus", "obediência, provisão e desejo de Deus pelo povo"),
    # NOVEMBRO
    ("Salmos 82", "Deus preside ao concílio divino", "justiça de Deus, defesa do oprimido"),
    ("Salmos 83", "Deus, não fiques em silêncio", "clamor contra inimigos, glória de Deus"),
    ("Salmos 85", "Restaura-nos, Deus da nossa salvação", "avivamento, misericórdia e paz"),
    ("Salmos 87", "Gloriosas coisas se falam de ti", "Sião, pertencimento e identidade no povo de Deus"),
    ("Salmos 88", "Clamei dia e noite", "sofrimento extremo, fidelidade na dor sem resolução"),
    ("Salmos 89", "Cantarei eternamente as misericórdias", "pacto de Davi, fidelidade e clamor"),
    ("Salmos 92", "Bom é louvar ao Senhor", "gratidão matinal, florescimento do justo"),
    ("Salmos 93", "O Senhor reina", "majestade de Deus, soberania e firmeza eterna"),
    ("Salmos 94", "Senhor, Deus das vinganças", "justiça de Deus, instrução pela disciplina"),
    ("Salmos 95", "Vinde, adoremos e prostremo-nos", "chamado à adoração, advertência da dureza do coração"),
    ("Salmos 96", "Cantai ao Senhor um cântico novo", "missão, criação que louva e glória de Deus"),
    ("Salmos 97", "O Senhor reina, alegre-se a terra", "teofania, luz do justo e alegria"),
    ("Salmos 98", "Cantai ao Senhor um cântico novo", "vitória, julgamento justo e alegria da criação"),
    ("Salmos 99", "O Senhor reina, os povos tremem", "santidade de Deus, intercessores e perdão"),
    ("Salmos 101", "Cantarei do amor e da justiça", "integridade, compromisso com a pureza"),
    ("Salmos 102", "Minha oração chegue até ti", "mortalidade, eternidade de Deus e restauração"),
    ("Salmos 104", "Benze ao Senhor, ó minha alma", "maravilhas da criação, dependência e louvor"),
    ("Salmos 105", "Dai graças ao Senhor", "memória das obras de Deus, fidelidade ao pacto"),
    ("Salmos 106", "Louvai ao Senhor", "infidelidade de Israel, misericórdia de Deus e confissão"),
    ("Salmos 108", "Acordai, alaúde e harpa", "confiança renovada, vitória com Deus"),
    ("Salmos 109", "Ó Deus do meu louvor", "clamor contra injustiça, socorro e gratidão"),
    ("Salmos 110", "O Senhor disse ao meu Senhor", "sacerdócio e reino de Cristo, vitória"),
    ("Salmos 111", "Louvarei ao Senhor de todo o coração", "obras de Deus, fidelidade e temor"),
    ("Salmos 113", "Louvai, servos do Senhor", "humildade de Deus, exaltação dos humildes"),
    ("Salmos 114", "Quando Israel saiu do Egito", "êxodo, presença de Deus e criação que treme"),
    ("Salmos 115", "A nós não, Senhor", "glória somente a Deus, ídolos e confiança"),
    ("Salmos 116", "Amo o Senhor que ouviu", "oração respondida, gratidão e voto cumprido"),
    ("Salmos 117", "Louvai ao Senhor, nações", "misericórdia universal, fidelidade eterna"),
    ("Salmos 118", "A pedra que os construtores rejeitaram", "vitória do rejeitado, rejoicing e força"),
    ("Salmos 119:97–112", "Lâmpada para os meus pés", "amor pela Palavra, sabedoria e orientação"),
    ("Salmos 120", "Em minha angústia clamei", "clamor, paz e habitação entre inimigos da paz"),
    # DEZEMBRO
    ("Salmos 122", "Alegrei-me quando me disseram", "amor pela casa de Deus, paz de Jerusalém"),
    ("Salmos 123", "Os nossos olhos estão no Senhor", "dependência, misericórdia e espera"),
    ("Salmos 124", "Se o Senhor não estivesse", "socorro de Deus, escape e nome do Senhor"),
    ("Salmos 125", "Os que confiam no Senhor", "estabilidade, proteção e paz sobre Israel"),
    ("Salmos 127", "Se o Senhor não edificar", "dependência de Deus no trabalho, família e missão"),
    ("Salmos 128", "Bem-aventurado todo que teme ao Senhor", "família, fruto e bênção geracional"),
    ("Salmos 129", "Muito me oprimiram desde a juventude", "perseverança, vitória sobre o passado"),
    ("Salmos 131", "Como criança desmamada", "humildade, contentamento e esperança em Deus"),
    ("Salmos 132", "Lembra-te de Davi", "fidelidade ao pacto, habitação de Deus e bênção"),
    ("Salmos 133", "Como é bom viver em unidade", "comunidade, unção e a bênção da unidade"),
    ("Salmos 134", "Louvai ao Senhor, todos os servos", "ministério noturno, bênção de Sião"),
    ("Salmos 135", "Louvai o nome do Senhor", "eleição, obras de Deus e futilidade dos ídolos"),
    ("Salmos 136", "A sua misericórdia dura para sempre", "refrão de graça, história de redenção"),
    ("Salmos 137", "Junto aos rios da Babilônia", "lamento no exílio, memória e amor por Sião"),
    ("Salmos 138", "De todo o coração te louvarei", "gratidão, humildade de Deus e proteção"),
    ("Salmos 140", "Livra-me, Senhor, do homem mau", "proteção divina, clamor e justiça"),
    ("Salmos 141", "Senhor, a ti clamo", "oração de guarda, boca e coração vigiados"),
    ("Salmos 142", "Clamo ao Senhor com minha voz", "desamparo, único refúgio e libertação"),
    ("Salmos 143", "Ouve a minha oração", "espírito abatido, memória das obras e renovação"),
    ("Salmos 144", "Bem-aventurado o povo cujo Deus é o Senhor", "proteção, provisão e identidade"),
    ("Salmos 146", "Não ponhais confiança em príncipes", "esperança em Deus, não em poder humano"),
    ("Salmos 147", "Bom é cantar louvores", "cura, restauração e Palavra que sustenta"),
    ("Salmos 148", "Louvai ao Senhor dos céus", "criação inteira em adoração, glória de Deus"),
    ("Salmos 149", "Cantai ao Senhor um cântico novo", "alegria do povo de Deus, louvor e vitória"),
    ("Salmos 150", "Louvai ao Senhor com trombeta", "louvor total, com tudo e em todo lugar"),
    ("Isaías 7", "A virgem conceberá", "sinal de Emanuel, presença de Deus conosco"),
    ("Isaías 11", "O ramo de Jessé", "o rei messiânico, paz no reino e o Espírito sobre ele"),
    ("Isaías 35", "O deserto florescerá", "restauração, alegria e o caminho da santidade"),
    ("Isaías 42", "O servo escolhido", "missão do servo, justiça e luz para as nações"),
    ("Isaías 44", "Não temas, eu te redimi", "identidade do povo de Deus, futilidade dos ídolos"),
    ("Isaías 48", "Eu sou o Senhor teu Deus", "instrução divina, paz como rio e saída da Babilônia"),
    ("Isaías 60", "Levanta-te, resplandece", "glória de Deus sobre o povo, luz nas trevas"),
]

# ============================================================
# SELECIONAR TEMA DO DIA (sem repetição no ano)
# ============================================================
BRT      = timezone(timedelta(hours=-3))
today    = datetime.now(BRT)
date_str = today.strftime("%d/%m/%Y")
day_of_year = today.timetuple().tm_yday  # 1 a 365

WEEKDAY_PT = {
    0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira",
    3: "quinta-feira",  4: "sexta-feira", 5: "sábado", 6: "domingo",
}
weekday = WEEKDAY_PT[today.weekday()]

tema_idx  = (day_of_year - 1) % len(TEMAS)
livro, tema_titulo, tema_foco = TEMAS[tema_idx]

PROMPT = f"""
Você é um pastor evangélico.
Hoje é {weekday}, {date_str}.
Livro/Passagem: {livro}
Tema: {tema_titulo}
Foco: {tema_foco}

Gere um devocional curto formatado EXATAMENTE assim para WhatsApp:

*✍️ [Título]*

📜 *Texto:* [versículo específico de {livro}] _(NVT)_

*🔍 Reflexão*
[2-3 linhas simples e diretas sobre o texto]

*🙏 Aplicação*
[1-2 linhas práticas para o dia]

*💭 Para Meditar*
_[Uma pergunta curta e objetiva]_

━━━━━━━━━━━━━━━━━
_Que a Palavra de Deus ilumine o seu dia!_ ☀️

Regras:
- Negrito com *asteriscos*, itálico com _underline_
- Tradução NVT
- Linguagem simples e direta
- Máximo 250 palavras no total
- Não inclua cabeçalho, apenas o conteúdo a partir do título
"""

# ============================================================
# GERAR DEVOCIONAL COM CLAUDE
# ============================================================
def generate_study():
    wait_time = 2
    for attempt in range(1, 5):
        try:
            print(f"Gerando devocional com Claude | tentativa {attempt}")
            print(f"Tema do dia ({day_of_year}/365): {livro} — {tema_titulo}")
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": PROMPT}],
                },
                timeout=60,
            )
            resp.raise_for_status()
            study = resp.json()["content"][0]["text"].strip()
            if not study:
                raise ValueError("Resposta vazia")
            print("Devocional gerado com sucesso!")
            return study
        except Exception as e:
            error_text = str(e).upper()
            if any(x in error_text for x in ["529", "503", "OVERLOADED", "TIMEOUT"]):
                print(f"Erro temporário ({e}). Nova tentativa em {wait_time}s")
                time.sleep(wait_time)
                wait_time *= 2
                continue
            raise
    raise Exception("Falha após várias tentativas")

# ============================================================
# ENVIAR PELA EVOLUTION API
# ============================================================
def send_whatsapp(message: str, number: str) -> None:
    url = f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_APIKEY,
    }
    payload = {
        "number": number,
        "text": message,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"Enviado para {number}: {resp.status_code}")
    except Exception as e:
        print(f"Erro ao enviar para {number}: {e}")

# ============================================================
# MAIN
# ============================================================
def main():
    try:
        study = generate_study()

        header = (
            f"🏄 *Bola de Neve Camaquã*\n"
            f"📖 *Devocional Diário*\n"
            f"_{weekday.capitalize()}, {date_str}_\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🏷️ *{tema_titulo}*\n"
            f"📖 _{livro}_\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
        )

        msg = header + study

        send_whatsapp(msg, PHONE_1)
        send_whatsapp(msg, PHONE_2)

        # Para ativar o grupo, remova o comentário abaixo:
        # send_whatsapp(msg, GROUP_ID)

        print("Devocional enviado com sucesso!")

    except Exception as e:
        error_msg = f"❌ Falha ao gerar o devocional.\n\nData: {date_str}\n\nErro: {str(e)}"
        send_whatsapp(error_msg, PHONE_1)
        print(f"Erro: {e}")
        raise

if __name__ == "__main__":
    main()