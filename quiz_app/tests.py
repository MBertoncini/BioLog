import csv
import os
import random
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.conf import settings
from .models import Species, Region, Month, QuizSession, QuizQuestion, SpeciesAreaWeight, SpeciesPeriodWeight, Observation, Image
from .views import get_difficult_species, get_score_distribution, get_performance_trend, get_common_errors
from .utils import get_weighted_random_species, get_next_observation
import logging
import io
import matplotlib.pyplot as plt
from collections import Counter
from scipy.stats import chisquare



class QuizAppTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("\nSetting up test data...")
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.stats_group = Group.objects.create(name='Statistics Viewers')
        cls.stats_user = User.objects.create_user(username='statsuser', password='12345')
        cls.stats_user.groups.add(cls.stats_group)

        cls.region = Region.objects.create(name='Test Region')
        cls.month = Month.objects.create(name='Test Month')
        
        # Carica specie e pesi dai CSV
        cls.load_species_from_csv('species.csv')
        cls.load_area_weights_from_csv('species_area_weights.csv')
        cls.load_period_weights_from_csv('species_period_weights.csv')

        # Crea alcune sessioni di quiz e domande per i test
        for i in range(5):
            session = QuizSession.objects.create(
                user=cls.user,
                score=i,
                total_questions=5,
                region=cls.region,
                month=cls.month,
                quiz_type='multiple_choice'
            )
            for j in range(5):
                species = Species.objects.all()[j % 2]
                QuizQuestion.objects.create(
                    quiz_session=session,
                    species=species,
                    is_correct=(j < i),
                    question_number=j+1
                )
        print("Test data setup complete.")

    @classmethod
    def load_species_from_csv(cls, file_name):
        file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Species.objects.create(
                    name=row['name'],
                    family=row['family'],
                    probability=float(row['probability'])
                )

    @classmethod
    def load_area_weights_from_csv(cls, file_name):
        file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                species = Species.objects.get(name=row['species'])
                for region_name, weight in row.items():
                    if region_name != 'species':
                        region, _ = Region.objects.get_or_create(name=region_name)
                        SpeciesAreaWeight.objects.create(
                            species=species,
                            region=region,
                            weight=float(weight)
                        )

    @classmethod
    def load_period_weights_from_csv(cls, file_name):
        file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                species = Species.objects.get(name=row['species'])
                for month_name, weight in row.items():
                    if month_name != 'species':
                        month, _ = Month.objects.get_or_create(name=month_name)
                        SpeciesPeriodWeight.objects.create(
                            species=species,
                            month=month,
                            weight=float(weight)
                        )

    def test_home_view(self):
        print("\nTesting home view...")
        response = self.client.get(reverse('quiz_app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quiz Farfalle')
        print("Home view test complete.")

    def test_start_quiz_view(self):
        print("\nTesting start quiz view...")
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('quiz_app:start_quiz', kwargs={'quiz_type': 'multiple_choice'}))
        self.assertEqual(response.status_code, 200)
        print("Start quiz view test complete.")

    def test_get_difficult_species(self):
        print("\nTesting get_difficult_species...")
        difficult_species = get_difficult_species()
        print(f"Number of difficult species: {len(difficult_species)}")
        self.assertGreater(len(difficult_species), 0)
        if len(difficult_species) > 1:
            self.assertGreater(difficult_species[0].error_rate, difficult_species[1].error_rate)
        print("Get difficult species test complete.")

    def test_get_score_distribution(self):
        print("\nTesting get_score_distribution...")
        distribution = get_score_distribution(QuizSession.objects.all())
        print(f"Score distribution: {distribution}")
        self.assertGreater(len(distribution), 0)
        print("Get score distribution test complete.")

    def test_get_performance_trend(self):
        print("\nTesting get_performance_trend...")
        trend = get_performance_trend()
        print(f"Performance trend: {trend}")
        self.assertEqual(len(trend), 1)
        print("Get performance trend test complete.")

    def test_get_common_errors(self):
        print("\nTesting get_common_errors...")
        errors = get_common_errors()
        print(f"Common errors: {errors}")
        self.assertLessEqual(len(errors), 20)
        print("Get common errors test complete.")

    def test_statistics_view(self):
        print("\nTesting statistics view...")
        self.client.login(username='statsuser', password='12345')
        response = self.client.get(reverse('quiz_app:statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Statistiche del Quiz')
        print("Statistics view test complete.")

    def test_download_statistics(self):
        print("\nTesting download statistics...")
        self.client.login(username='statsuser', password='12345')
        response = self.client.get(reverse('quiz_app:download_all_statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        print("Download statistics test complete.")


    def test_get_weighted_random_species(self):
        print("\nTesting question generation...")
        region = Region.objects.first()
        month = Month.objects.first()
        
        species, weight = get_weighted_random_species(region, month)
        
        if species is None:
            print("No species returned")
            self.assertEqual(weight, 0)  # Cambiato da self.assertIsNone(weight)
        else:
            print(f"Selected species: {species.name}, Weight: {weight}")
            self.assertIsNotNone(species)
            self.assertGreater(weight, 0)
        
        print("Question generation test complete.")


import csv
from collections import Counter
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Species, Region, Month, SpeciesAreaWeight, SpeciesPeriodWeight
from .utils import get_weighted_random_species

class QuizDistributionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("\nSetting up test data...")
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.stats_group = Group.objects.create(name='Statistics Viewers')
        cls.stats_user = User.objects.create_user(username='statsuser', password='12345')
        cls.stats_user.groups.add(cls.stats_group)

        cls.load_regions()
        cls.load_months()
        cls.load_species()
        cls.load_area_weights()
        cls.load_period_weights()

        # Create some quiz sessions and questions for testing
        for i in range(5):
            session = QuizSession.objects.create(
                user=cls.user,
                score=i,
                total_questions=5,
                region=Region.objects.first(),
                month=Month.objects.first(),
                quiz_type='multiple_choice'
            )
            for j in range(5):
                species = Species.objects.all()[j % 2]
                QuizQuestion.objects.create(
                    quiz_session=session,
                    species=species,
                    is_correct=(j < i),
                    question_number=j+1
                )
        print("Test data setup complete.")

    @classmethod
    def load_csv(cls, filename):
        with open(f'data/{filename}', 'r') as f:
            return list(csv.DictReader(f))

    @classmethod
    def load_regions(cls):
        regions_data = cls.load_csv('regions.csv')
        for row in regions_data:
            Region.objects.create(name=row['name'])

    @classmethod
    def load_months(cls):
        months_data = cls.load_csv('months.csv')
        for row in months_data:
            Month.objects.create(name=row['name'])

    @classmethod
    def load_species(cls):
        species_data = cls.load_csv('species.csv')
        for row in species_data:
            Species.objects.create(
                name=row['name'],
                family=row['family'],
                probability=float(row['probability'])
            )

    @classmethod
    def load_area_weights(cls):
        weights_data = cls.load_csv('species_area_weights.csv')
        for row in weights_data:
            species = Species.objects.get(name=row['species'])
            for region_name, weight in row.items():
                if region_name != 'species':
                    region, created = Region.objects.get_or_create(name=region_name)
                    SpeciesAreaWeight.objects.create(
                        species=species,
                        region=region,
                        weight=float(weight)
                    )

    @classmethod
    def load_period_weights(cls):
        weights_data = cls.load_csv('species_period_weights.csv')
        for row in weights_data:
            species = Species.objects.get(name=row['species'])
            for month_name, weight in row.items():
                if month_name != 'species':
                    month, created = Month.objects.get_or_create(name=month_name)
                    SpeciesPeriodWeight.objects.create(
                        species=species,
                        month=month,
                        weight=float(weight)
                    )

    def test_home_view(self):
        print("\nTesting home view...")
        response = self.client.get(reverse('quiz_app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quiz Farfalle')
        print("Home view test complete.")

    def test_start_quiz_view(self):
        print("\nTesting start quiz view...")
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('quiz_app:start_quiz', kwargs={'quiz_type': 'multiple_choice'}))
        self.assertEqual(response.status_code, 200)
        print("Start quiz view test complete.")

    def test_get_difficult_species(self):
        print("\nTesting get_difficult_species...")
        difficult_species = get_difficult_species()
        print(f"Number of difficult species: {len(difficult_species)}")
        self.assertGreater(len(difficult_species), 0)
        if len(difficult_species) > 1:
            self.assertGreater(difficult_species[0].error_rate, difficult_species[1].error_rate)
        print("Get difficult species test complete.")

    def test_get_score_distribution(self):
        print("\nTesting get_score_distribution...")
        distribution = get_score_distribution(QuizSession.objects.all())
        print(f"Score distribution: {distribution}")
        self.assertGreater(len(distribution), 0)
        print("Get score distribution test complete.")

    def test_get_performance_trend(self):
        print("\nTesting get_performance_trend...")
        trend = get_performance_trend()
        print(f"Performance trend: {trend}")
        self.assertEqual(len(trend), 1)
        print("Get performance trend test complete.")

    def test_get_common_errors(self):
        print("\nTesting get_common_errors...")
        errors = get_common_errors()
        print(f"Common errors: {errors}")
        self.assertLessEqual(len(errors), 20)
        print("Get common errors test complete.")

    def test_statistics_view(self):
        print("\nTesting statistics view...")
        self.client.login(username='statsuser', password='12345')
        response = self.client.get(reverse('quiz_app:statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Statistiche del Quiz')
        print("Statistics view test complete.")

    def test_species_distribution(self):
        print("\nTesting species distribution...")
        num_simulations = 15000
        region = Region.objects.first()
        month = Month.objects.first()
        species_counts = Counter()
        total_weight = 0

        # Calculate expected probabilities
        expected_probabilities = {}
        for species in Species.objects.all():
            area_weight = SpeciesAreaWeight.objects.get(species=species, region=region).weight
            period_weight = SpeciesPeriodWeight.objects.get(species=species, month=month).weight
            expected_probabilities[species.name] = species.probability * area_weight * period_weight
        
        # Normalize expected probabilities
        total_prob = sum(expected_probabilities.values())
        expected_probabilities = {name: prob/total_prob for name, prob in expected_probabilities.items()}

        for _ in range(num_simulations):
            species, weight = get_weighted_random_species(region, month)
            if species:
                species_counts[species.name] += 1
                total_weight += weight

        observed_distribution = {name: count/num_simulations for name, count in species_counts.items()}
        average_weight = total_weight / num_simulations if total_weight > 0 else 0

        print(f"Average weight: {average_weight:.4f}")
        print("\nTop 20 most frequently selected species:")
        for name, prob in sorted(observed_distribution.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"{name}: {prob:.4f}")

        # Statistical analysis
        expected_counts = {name: max(prob * num_simulations, 1) for name, prob in expected_probabilities.items()}
        observed_counts = {name: max(prob * num_simulations, 1) for name, prob in observed_distribution.items()}

        # Ensure keys are in the same order
        keys = list(set(expected_counts.keys()) | set(observed_counts.keys()))
        expected = [expected_counts.get(k, 1) for k in keys]
        observed = [observed_counts.get(k, 1) for k in keys]

        try:
            chi2, p_value = chisquare(f_obs=observed, f_exp=expected)
            print(f"Chi-square test p-value: {p_value}")
            self.assertGreater(p_value, 0.05, f"The observed distribution is significantly different from the expected (p-value: {p_value})")
        except ValueError as e:
            print(f"Chi-square test failed: {str(e)}")
            self.fail("Chi-square test failed due to invalid input data")

        # Analyze discrepancies
        discrepancies = []
        for species in Species.objects.all():
            expected_prob = expected_probabilities[species.name]
            observed_prob = observed_distribution.get(species.name, 0)
            discrepancy = abs(expected_prob - observed_prob) / expected_prob if expected_prob > 0 else 0
            discrepancies.append((species.name, discrepancy))

        print("\nTop 10 species with largest discrepancy:")
        for name, disc in sorted(discrepancies, key=lambda x: x[1], reverse=True)[:10]:
            print(f"{name}: {disc:.2f}")

        # Verify probabilities
        for species in Species.objects.all():
            expected_prob = expected_probabilities[species.name]
            observed_prob = observed_distribution.get(species.name, 0)
            self.assertAlmostEqual(expected_prob, observed_prob, delta=0.15 * expected_prob, 
                                msg=f"Inconsistent probability for {species.name}. Expected: {expected_prob:.4f}, Observed: {observed_prob:.4f}")

        print("Species distribution test complete.")

    def plot_distributions(self, expected, observed):
        plt.figure(figsize=(15, 10))
        plt.bar(range(len(expected)), expected.values(), alpha=0.5, label='Expected')
        plt.bar(range(len(observed)), observed.values(), alpha=0.5, label='Observed')
        plt.legend()
        plt.xticks(range(len(expected)), expected.keys(), rotation='vertical')
        plt.tight_layout()
        plt.savefig('distribution_comparison.png')
        plt.close()