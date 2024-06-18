from unittest.mock import call, patch
from django.urls import reverse
from django.test import TestCase
from prometheus_client.parser import text_string_to_metric_families
from zentral.contrib.santa.models import Rule, Target, translate_rule_policy
from zentral.conf import settings
from .utils import force_configuration, force_enrolled_machine, force_rule, force_target_counter


class SantaMetricsViewsTestCase(TestCase):
    # utility methods

    def _make_authenticated_request(self):
        return self.client.get(reverse("santa_metrics:all"),
                               HTTP_AUTHORIZATION=f'Bearer {settings["api"]["metrics_bearer_token"]}')

    # metrics

    def test_metrics_permission_denied(self):
        response = self.client.get(reverse("santa_metrics:all"))
        self.assertEqual(response.status_code, 403)

    def test_metrics_permission_ok(self):
        response = self._make_authenticated_request()
        self.assertEqual(response.status_code, 200)

    def test_configurations(self):
        config_m = force_configuration(lockdown=False)
        config_l = force_configuration(lockdown=True)
        response = self._make_authenticated_request()
        for family in text_string_to_metric_families(response.content.decode("utf-8")):
            if family.name != "zentral_santa_configurations_info":
                continue
            else:
                self.assertEqual(len(family.samples), 2)
                for sample in family.samples:
                    self.assertEqual(sample.value, 1)
                    if int(sample.labels["pk"]) == config_m.pk:
                        self.assertEqual(sample.labels["mode"], "MONITOR")
                        self.assertEqual(sample.labels["name"], config_m.name)
                    elif int(sample.labels["pk"]) == config_l.pk:
                        self.assertEqual(sample.labels["mode"], "LOCKDOWN")
                        self.assertEqual(sample.labels["name"], config_l.name)
                    else:
                        raise AssertionError("Unknown config")
                break
        else:
            raise AssertionError("could not find expected metric family")
        self.assertEqual(response.status_code, 200)

    @patch("zentral.contrib.santa.metrics_views.connection")
    @patch("zentral.contrib.santa.metrics_views.logger.warning")
    def test_configurations_info_unknown_mode(self, warning, connection):
        mocked_fetchall = connection.cursor.return_value.__enter__.return_value.fetchall
        mocked_fetchall.side_effect = [
            [(1, "yolo", 42)],  # 1st call with bad mode
            [],  # 2nd call for the enrolled machines gauge
            [],  # 3rd call for the rules gauge
            [],  # 4th call for the targets gauge
        ]
        response = self._make_authenticated_request()
        family_count = 0
        sample_count = 0
        for family in text_string_to_metric_families(response.content.decode("utf-8")):
            if family.name != "zentral_santa_configurations_info":
                continue
            family_count += 1
            sample_count += len(family.samples)
        self.assertEqual(family_count, 1)
        self.assertEqual(sample_count, 0)
        warning.assert_called_once_with("Unknown santa configuration mode: %s", 42)
        self.assertEqual(mocked_fetchall.mock_calls, [call() for _ in range(4)])

    def test_enrolled_machines(self):
        em_m = force_enrolled_machine(lockdown=False, santa_version="2024.5")
        em_l = force_enrolled_machine(lockdown=True, santa_version="2024.6")
        response = self._make_authenticated_request()
        for family in text_string_to_metric_families(response.content.decode("utf-8")):
            if family.name != "zentral_santa_enrolled_machines_total":
                continue
            else:
                self.assertEqual(len(family.samples), 2)
                for sample in family.samples:
                    self.assertEqual(sample.value, 1)
                    cfg_pk = int(sample.labels["cfg_pk"])
                    if cfg_pk == em_m.enrollment.configuration.pk:
                        self.assertEqual(sample.labels["mode"], "MONITOR")
                        self.assertEqual(sample.labels["santa_version"], "2024.5")
                    elif cfg_pk == em_l.enrollment.configuration.pk:
                        self.assertEqual(sample.labels["mode"], "LOCKDOWN")
                        self.assertEqual(sample.labels["santa_version"], "2024.6")
                    else:
                        raise AssertionError("Unknown enrolled machine")
                break
        else:
            raise AssertionError("could not find expected metric family")
        self.assertEqual(response.status_code, 200)

    @patch("zentral.contrib.santa.metrics_views.connection")
    @patch("zentral.contrib.santa.metrics_views.logger.warning")
    def test_enrolled_machines_unknown_mode(self, warning, connection):
        mocked_fetchall = connection.cursor.return_value.__enter__.return_value.fetchall
        mocked_fetchall.side_effect = [
            [],  # 1st call for the configurations info gauge
            [(1, 42, "2024.5", 1)],  # 2nd call for the enrolled machines gauge
            [],  # 3rd call for the rules gauge
            [],  # 4th call for the targets gauge
        ]
        response = self._make_authenticated_request()
        family_count = 0
        sample_count = 0
        for family in text_string_to_metric_families(response.content.decode("utf-8")):
            if family.name != "zentral_santa_enrolled_machines_total":
                continue
            family_count += 1
            sample_count += len(family.samples)
        self.assertEqual(family_count, 1)
        self.assertEqual(sample_count, 0)
        warning.assert_called_once_with("Unknown santa configuration mode: %s", 42)
        self.assertEqual(mocked_fetchall.mock_calls, [call() for _ in range(4)])

    def test_rules(self):
        rules = {}
        for target_type, policy in (
            (Target.BINARY, Rule.ALLOWLIST),
            (Target.BUNDLE, Rule.BLOCKLIST),
            (Target.CDHASH, Rule.ALLOWLIST_COMPILER),
            (Target.CERTIFICATE, Rule.SILENT_BLOCKLIST),
            (Target.TEAM_ID, Rule.ALLOWLIST),
            (Target.SIGNING_ID, Rule.BLOCKLIST),
        ):
            rule = force_rule(target_type=target_type, policy=policy)
            rules[str(rule.configuration.pk)] = rule
        response = self._make_authenticated_request()
        for family in text_string_to_metric_families(response.content.decode("utf-8")):
            if family.name != "zentral_santa_rules_total":
                continue
            else:
                self.assertEqual(len(family.samples), 6)
                for sample in family.samples:
                    self.assertEqual(sample.value, 1)
                    self.assertEqual(sample.labels["ruleset"], "_")
                    rule = rules[sample.labels["cfg_pk"]]
                    self.assertEqual(sample.labels["policy"], translate_rule_policy(rule.policy))
                    self.assertEqual(sample.labels["target_type"], rule.target.type)
                break
        else:
            raise AssertionError("could not find expected metric family")
        self.assertEqual(response.status_code, 200)

    @patch("zentral.contrib.santa.metrics_views.connection")
    @patch("zentral.contrib.santa.metrics_views.logger.error")
    def test_rules_unknown_policy(self, warning, connection):
        mocked_fetchall = connection.cursor.return_value.__enter__.return_value.fetchall
        mocked_fetchall.side_effect = [
            [],  # 1st call for the configurations info
            [],  # 2nd call for the enrolled machines gauge
            [(1, None, "BUNDLE", 42, 1)],  # 3rd call with unknown policy
            [],  # 4th call for the targets gauge
        ]
        response = self._make_authenticated_request()
        family_count = 0
        sample_count = 0
        for family in text_string_to_metric_families(response.content.decode("utf-8")):
            if family.name != "zentral_santa_rules_total":
                continue
            family_count += 1
            sample_count += len(family.samples)
        self.assertEqual(family_count, 1)
        self.assertEqual(sample_count, 0)
        warning.assert_called_once_with("Unknown rule policy: %s", 42)
        self.assertEqual(mocked_fetchall.mock_calls, [call() for _ in range(4)])

    def test_targets(self):
        target_counters = {}
        for target_type, blocked_count, collected_count, executed_count, is_rule in (
            (Target.BINARY, 11, 0, 0, True),
            (Target.BUNDLE, 11, 22, 0, False),
            (Target.CDHASH, 11, 22, 33, False),
            (Target.CERTIFICATE, 1, 0, 0, False),
            (Target.TEAM_ID, 1, 2, 0, False),
            (Target.SIGNING_ID, 1, 2, 3, True),
        ):
            target_counter = force_target_counter(
                target_type,
                blocked_count=blocked_count,
                collected_count=collected_count,
                executed_count=executed_count,
                is_rule=is_rule,
            )
            target_counters.setdefault(str(target_counter.configuration.pk), {})[target_counter.target.type] = {
                "total": 1,
                "blocked_total": blocked_count,
                "collected_total": collected_count,
                "executed_total": executed_count,
                "rules_total": 1 if is_rule else 0
            }
        response = self._make_authenticated_request()
        family_count = 0
        total_keys = set()
        for family in text_string_to_metric_families(response.content.decode("utf-8")):
            if not family.name.startswith("zentral_santa_targets_"):
                continue
            family_count += 1
            total_key = family.name.removeprefix("zentral_santa_targets_")
            total_keys.add(total_key)
            sample_count = 0
            for sample in family.samples:
                sample_count += 1
                self.assertEqual(
                    sample.value,
                    target_counters[sample.labels["cfg_pk"]][sample.labels["type"]][total_key]
                )
            self.assertEqual(sample_count, 6)
        self.assertEqual(family_count, 5)
        self.assertEqual(
            total_keys,
            {"total", "blocked_total", "collected_total", "executed_total", "rules_total"}
        )
