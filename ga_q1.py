# app.py
import random
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# ---------------------------------
# Fixed GA Parameters (from PDF)
# ---------------------------------
POP_SIZE = 300          # Population = 300
CHROM_LEN = 80          # Chromosome Length = 80
TARGET_ONES = 40        # Fitness peaks at ones = 40
MAX_FITNESS = 80        # Max fitness = 80
N_GENERATIONS = 50      # Generations = 50

# ---------------------------------
# GA Hyperparameters
# ---------------------------------
TOURNAMENT_K = 3
CROSSOVER_RATE = 0.9
MUTATION_RATE = 1.0 / CHROM_LEN

# ---------------------------------
# Fitness Function
# ---------------------------------
def fitness(individual):
    """
    Fitness is maximum (80) when number of ones = 40
    """
    ones = individual.sum()
    return MAX_FITNESS - abs(ones - TARGET_ONES)

# ---------------------------------
# GA Operators
# ---------------------------------
def init_population(pop_size, chrom_len):
    return np.random.randint(0, 2, size=(pop_size, chrom_len))

def tournament_selection(pop, fits, k):
    selected = np.random.randint(0, len(pop), k)
    best = selected[np.argmax(fits[selected])]
    return pop[best].copy()

def single_point_crossover(p1, p2):
    if np.random.rand() > CROSSOVER_RATE:
        return p1.copy(), p2.copy()
    point = np.random.randint(1, CHROM_LEN)
    c1 = np.concatenate([p1[:point], p2[point:]])
    c2 = np.concatenate([p2[:point], p1[point:]])
    return c1, c2

def mutate(individual):
    for i in range(CHROM_LEN):
        if np.random.rand() < MUTATION_RATE:
            individual[i] = 1 - individual[i]
    return individual

def evolve(population, generations):
    best_fitness_curve = []
    best_individual = None
    best_fitness = -1

    for _ in range(generations):
        fits = np.array([fitness(ind) for ind in population])

        gen_best_idx = np.argmax(fits)
        gen_best_fit = fits[gen_best_idx]
        best_fitness_curve.append(gen_best_fit)

        if gen_best_fit > best_fitness:
            best_fitness = gen_best_fit
            best_individual = population[gen_best_idx].copy()

        new_population = []
        while len(new_population) < len(population):
            p1 = tournament_selection(population, fits, TOURNAMENT_K)
            p2 = tournament_selection(population, fits, TOURNAMENT_K)
            c1, c2 = single_point_crossover(p1, p2)
            new_population.append(mutate(c1))
            new_population.append(mutate(c2))

        population = np.array(new_population[:len(population)])

    return best_individual, best_fitness, best_fitness_curve

# ---------------------------------
# Streamlit UI
# ---------------------------------
st.set_page_config(page_title="Genetic Algorithm Bit Pattern Generator", layout="centered")

st.title("🧬 Genetic Algorithm Bit Pattern Generator")
st.caption(
    "Population = 300 | Chromosome Length = 80 | Generations = 50\n"
    "Fitness peaks at 40 ones with maximum fitness = 80"
)

seed = st.number_input("Random Seed", value=42, step=1)
run = st.button("Run Genetic Algorithm", type="primary")

if run:
    random.seed(seed)
    np.random.seed(seed)

    population = init_population(POP_SIZE, CHROM_LEN)
    best_ind, best_fit, curve = evolve(population, N_GENERATIONS)

    ones = int(best_ind.sum())
    zeros = CHROM_LEN - ones
    bitstring = "".join(map(str, best_ind))

    st.subheader("🏁 Best Individual Found")
    st.metric("Best Fitness", best_fit)
    st.write(f"**Ones:** {ones} | **Zeros:** {zeros}")
    st.code(bitstring, language="text")

    st.subheader("📈 Fitness Convergence")
    fig, ax = plt.subplots()
    ax.plot(range(1, N_GENERATIONS + 1), curve)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Best Fitness")
    ax.set_title("GA Convergence Curve")
    ax.grid(True)
    st.pyplot(fig)

    if best_fit == MAX_FITNESS and ones == TARGET_ONES:
        st.success("Optimal solution found (40 ones, fitness = 80) ✅")
    else:
        st.info("Near-optimal solution found. Try a different seed.")
