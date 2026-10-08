import copy

import pytest
import yaml

import content
import verhaal


def _schrijf(tmp_path, data):
    pad = tmp_path / "module.yaml"
    pad.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return pad


@pytest.fixture
def module_data():
    return copy.deepcopy(content.load_module())


def test_module_laadt_en_volgt_het_stramien():
    module = content.load_module()
    stappen = module["stappen"]
    assert len(stappen) == 6
    assert [(s["type"], s["rol"]) for s in stappen] == content.STRAMIEN


def test_module_zonder_bom():
    assert not content.MODULE_PAD.read_bytes().startswith(b"\xef\xbb\xbf")


def test_elk_skelet_invulbaar_met_fallback():
    module = content.load_module()
    for antwoord in [None, {"gedeeld": ["Een foto"], "gevoelig": "Ja"}]:
        velden = {**verhaal.FALLBACK, **verhaal.afgeleid(verhaal.FALLBACK, module, antwoord)}
        for stap in verhaal.vul_stappen(module["stappen"], velden):
            for veld in ("titel", "verhaal", "einde"):
                if stap.get(veld):
                    assert "{" not in stap[veld] and "}" not in stap[veld]
                    assert "\n\n\n" not in stap[veld]


def test_ontbrekend_veld_geeft_valueerror(tmp_path, module_data):
    del module_data["stappen"][2]["leerdoel"]
    with pytest.raises(ValueError, match="leerdoel"):
        content.load_module(_schrijf(tmp_path, module_data))


def test_verkeerd_stramien_geeft_valueerror(tmp_path, module_data):
    module_data["stappen"][1]["type"] = "verdieping"
    with pytest.raises(ValueError, match="stramien"):
        content.load_module(_schrijf(tmp_path, module_data))


def test_onbekend_invulveld_geeft_valueerror(tmp_path, module_data):
    module_data["stappen"][0]["verhaal"] += " {bestaat_niet}"
    with pytest.raises(ValueError, match="invulbaar"):
        content.load_module(_schrijf(tmp_path, module_data))


def test_ontbrekende_categoriezin_geeft_valueerror(tmp_path, module_data):
    del module_data["categorie_zinnen"]["beroepsgeheim"]
    with pytest.raises(ValueError, match="categorie_zinnen"):
        content.load_module(_schrijf(tmp_path, module_data))


def test_quiz_correct_buiten_bereik_geeft_valueerror(tmp_path, module_data):
    module_data["stappen"][5]["quiz"][0]["correct"] = 9
    with pytest.raises(ValueError, match="correct"):
        content.load_module(_schrijf(tmp_path, module_data))
