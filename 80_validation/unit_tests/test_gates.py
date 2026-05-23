"""Unit tests for JW + Magarada + Catatu gate filters."""
import pytest
from jw_quarantine_filter import is_jw_source, extract_jw_sources
from magarada_preliminary_gate import is_magarada_source, extract_magarada_sources
from catatu_archival_gate import is_catatu_source, extract_catatu_sources


class TestJWFilter:
    @pytest.mark.parametrize("src", [
        "jw_corroborated",
        "watch_tower_2013",
        "Watch Tower Bible and Tract Society",
        "WatchTower",
        "watch-tower",
        "NWT_2013",
        "nwt-genesis",
        "new_world_translation",
        "Nisamina_Religious_Corpus_Distillation_2026.05",
        "religious_corpus_distillation",
        "kingdom_hall_pub",
        "jehovahs_witnesses_archive",
        "jehovah's_witness_2020",
    ])
    def test_jw_sources_matched(self, src):
        assert is_jw_source(src), f"Should match JW: {src!r}"

    @pytest.mark.parametrize("src", [
        "foundry_v5",
        "Hererun_Wagüchagu_Dimurei_Agei_Garifuna",
        "BSB",
        "V_VAULT_director_attested",
        "Cambridge_UP_2023",
        "Hadel_1975",
        "Suazo_Pildoritas",
        "lgd_living_dictionary",
        "Magarada_Garifuna_Songs",
        "AILLA_Broach_2015",
    ])
    def test_non_jw_sources_not_matched(self, src):
        assert not is_jw_source(src), f"Should NOT match JW: {src!r}"

    def test_partition(self):
        srcs = ["foundry_v5", "watch_tower_2013", "BSB", "nwt_genesis", "Hadel_1975"]
        jw, nonjw = extract_jw_sources(srcs)
        assert jw == {"watch_tower_2013", "nwt_genesis"}
        assert nonjw == {"foundry_v5", "BSB", "Hadel_1975"}

    def test_empty_input(self):
        assert not is_jw_source("")
        assert not is_jw_source(None)


class TestMagaradaFilter:
    @pytest.mark.parametrize("src", [
        "magarada_unbroken_thread_PRELIMINARY",
        "Magarada_Stories",
        "shaka_magarada_attest",
        "About_Me_Shaka_Magarada",
        "unbroken_thread_novel",
        "magarada-stor",  # variant
    ])
    def test_magarada_preliminary_matched(self, src):
        assert is_magarada_source(src), f"Should match Magarada PRELIMINARY: {src!r}"

    @pytest.mark.parametrize("src", [
        "Magarada_Garifuna_Songs_text_Images",  # songs — consent_001 granted
        "magarada_songs_2026",                   # songs allowlist
        "magarada_garifuna_songs",
    ])
    def test_magarada_songs_NOT_matched(self, src):
        """Songs carry consent_001 granted; must NOT trigger PRELIMINARY gate."""
        assert not is_magarada_source(src), f"Songs should be allowed: {src!r}"

    @pytest.mark.parametrize("src", [
        "foundry_v5", "BSB", "V_VAULT_director_attested", "Hadel_1975",
    ])
    def test_non_magarada_not_matched(self, src):
        assert not is_magarada_source(src), f"Should NOT match Magarada: {src!r}"

    def test_partition(self):
        srcs = ["foundry_v5", "magarada_stories", "Magarada_Songs", "BSB", "unbroken_thread"]
        mag, nonmag = extract_magarada_sources(srcs)
        assert "magarada_stories" in mag
        assert "unbroken_thread" in mag
        # Songs do NOT match the PRELIMINARY gate
        assert "Magarada_Songs" not in mag


class TestCatatuFilter:
    @pytest.mark.parametrize("src", [
        "catatu_midwife_5890",
        "AILLA_Catatu_recording",
        "midwifery_interview_03",
        "5890_midwifery",
    ])
    def test_catatu_matched(self, src):
        assert is_catatu_source(src), f"Should match Catatu: {src!r}"

    @pytest.mark.parametrize("src", [
        "foundry_v5", "BSB", "Broach_2015_AILLA", "Hadel_1975",
    ])
    def test_non_catatu_not_matched(self, src):
        assert not is_catatu_source(src), f"Should NOT match Catatu: {src!r}"
