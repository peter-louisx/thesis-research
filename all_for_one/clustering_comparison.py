"""
=============================================================================
 CLUSTERING ALGORITHM COMPARISON PIPELINE
 Algorithms: K-Means, DBSCAN, SOM (MiniSom), GMM, Mean Shift, BERTopic
 Embeddings: paraphrase-multilingual-MiniLM-L12-v2 (sentence-transformers)
=============================================================================
"""

import os
import time
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import ListedColormap
from pathlib import Path

from sklearn.neighbors import NearestNeighbors

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  CONFIG — tweak these as needed
# ─────────────────────────────────────────────
EMBEDDING_MODEL   = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_CACHE   = Path("embeddings_cache.npy")
TEXT_CACHE        = Path("texts_cache.npy")
N_CLUSTERS        = 20          # used by K-Means, GMM, SOM
DBSCAN_EPS        = 0.5
DBSCAN_MIN_SAMPLES = 5
MEAN_SHIFT_BW     = None       # None = estimate automatically
SOM_GRID_X        = 15
SOM_GRID_Y        = 15
SOM_ITERATIONS    = 1000
BERTOPIC_MIN_TOPIC = 50
UMAP_COMPONENTS   = 2          # 2 or 3 for visualisation
RANDOM_STATE      = 42
FIGURE_DPI        = 150
OUTPUT_DIR        = Path("clustering_results")

OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# 1. DATA LOADING
# =============================================================================

def load_sample_tweets() -> list[str]:
    """
    Returns a small built-in tweet sample so the script runs without a CSV.
    Replace / extend this with your real data source.
    """
    tweets = [
        # politics
        "Pemerintah harus segera menangani masalah korupsi yang merajalela",
        "Pemilu 2024 harus berlangsung dengan jujur dan adil",
        "Kebijakan ekonomi pemerintah belum berpihak pada rakyat kecil",
        "DPR perlu lebih transparan dalam membuat undang-undang",
        "Presiden harus turun tangan mengatasi konflik di Papua",
        "Demokrasi Indonesia masih perlu banyak perbaikan",
        # economy
        "Harga bahan pokok terus naik, rakyat makin susah",
        "Inflasi 2024 diprediksi mencapai angka tertinggi",
        "UMKM butuh modal murah agar bisa berkembang",
        "Investasi asing diperlukan untuk mempercepat pertumbuhan ekonomi",
        "Nilai tukar rupiah melemah terhadap dolar AS",
        "Subsidi BBM perlu dikaji ulang agar tepat sasaran",
        # technology
        "AI akan mengubah cara kita bekerja secara fundamental",
        "Startup teknologi Indonesia semakin bersaing di kancah global",
        "Keamanan data pribadi harus menjadi prioritas utama",
        "Transformasi digital UMKM terhambat minimnya literasi teknologi",
        "5G akan membuka peluang bisnis baru di Indonesia",
        "Hacker makin canggih, perusahaan harus waspada",
        # health
        "Layanan BPJS masih banyak yang perlu diperbaiki",
        "Pandemi COVID-19 mengajarkan pentingnya sistem kesehatan yang kuat",
        "Stunting pada anak masih menjadi masalah serius di Indonesia",
        "Obat-obatan generik harus lebih mudah diakses masyarakat",
        "Kesehatan mental remaja sering diabaikan oleh orang tua",
        "Rumah sakit daerah kekurangan tenaga dokter spesialis",
        # environment
        "Kebakaran hutan merusak paru-paru bumi kita",
        "Sampah plastik laut mengancam ekosistem laut Indonesia",
        "Energi terbarukan harus segera menggantikan bahan bakar fosil",
        "Banjir tahunan Jakarta akibat kurangnya daerah resapan air",
        "Pembangunan infrastruktur harus memperhatikan lingkungan hidup",
        "Deforestasi Kalimantan terus berlanjut meski ada larangan",
        # education
        "Kualitas pendidikan di daerah terpencil masih sangat tertinggal",
        "Kurikulum Merdeka Belajar masih menuai pro dan kontra",
        "Beasiswa pelajar kurang mampu perlu diperluas jangkauannya",
        "Guru honorer masih banyak yang belum sejahtera",
        "Literasi digital siswa SD harus ditingkatkan sejak dini",
        "Perguruan tinggi harus menghasilkan lulusan yang siap kerja",
    ]
    # duplicate to give more data points
    return tweets * 5


def load_tweets_from_csv(csv_path: str, text_column: str = "text") -> list[str]:
    """Load tweets from a CSV file."""
    df = pd.read_csv(csv_path)
    return df[text_column].dropna().tolist()


# =============================================================================
# 2. EMBEDDING (with cache)
# =============================================================================

def get_embeddings(texts: list[str],
                   model_name: str = EMBEDDING_MODEL,
                   cache_path: Path = EMBEDDING_CACHE,
                   texts_cache_path: Path = TEXT_CACHE) -> np.ndarray:
    """
    Encode texts with sentence-transformers.
    Saves / loads a .npy cache so re-runs are instant.
    """
    if cache_path.exists() and texts_cache_path.exists():
        cached_texts = np.load(texts_cache_path, allow_pickle=True).tolist()
        if cached_texts == texts:
            print(f"[Cache] Loading embeddings from {cache_path}")
            return np.load(cache_path)

    print(f"[Embedding] Encoding {len(texts)} texts with '{model_name}' …")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    t0 = time.time()
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    print(f"[Embedding] Done in {time.time()-t0:.1f}s — shape {embeddings.shape}")

    np.save(cache_path, embeddings)
    np.save(texts_cache_path, np.array(texts, dtype=object))
    print(f"[Cache] Saved to {cache_path}")
    return embeddings


# =============================================================================
# 3. DIMENSIONALITY REDUCTION (visualisation only)
# =============================================================================

def reduce_dimensions(embeddings: np.ndarray,
                      method: str = "umap",
                      n_components: int = UMAP_COMPONENTS) -> np.ndarray:
    """UMAP (preferred) or PCA for 2D / 3D scatter visualisation."""
    print(f"[DimReduce] Running {method.upper()} → {n_components}D …")
    if method.lower() == "umap":
        try:
            import umap
            reducer = umap.UMAP(n_components=n_components,
                                random_state=RANDOM_STATE,
                                n_neighbors=15,
                                min_dist=0.1)
            return reducer.fit_transform(embeddings)
        except ImportError:
            print("[Warning] umap-learn not installed, falling back to PCA.")
            method = "pca"

    from sklearn.decomposition import PCA
    return PCA(n_components=n_components,
               random_state=RANDOM_STATE).fit_transform(embeddings)


# =============================================================================
# 4. CLUSTERING ALGORITHMS
# =============================================================================

def run_kmeans(embeddings: np.ndarray,
               n_clusters: int = N_CLUSTERS) -> np.ndarray:
    """K-Means clustering."""
    from sklearn.cluster import KMeans
    print(f"[K-Means] k={n_clusters}")
    model = KMeans(n_clusters=n_clusters,
                   random_state=RANDOM_STATE,
                   n_init="auto")
    return model.fit_predict(embeddings)


def run_dbscan(embeddings: np.ndarray,
               eps: float = DBSCAN_EPS,
               min_samples: int = DBSCAN_MIN_SAMPLES) -> np.ndarray:
    """DBSCAN clustering. Label -1 = noise."""
    from sklearn.cluster import DBSCAN
    print(f"[DBSCAN] eps={eps}, min_samples={min_samples}")
    model = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)
    return model.fit_predict(embeddings)


def run_som(embeddings: np.ndarray,
            grid_x: int = SOM_GRID_X,
            grid_y: int = SOM_GRID_Y,
            iterations: int = SOM_ITERATIONS) -> np.ndarray:
    """Self-Organising Map via MiniSom. Returns BMU (Best Matching Unit) cluster ID."""
    from minisom import MiniSom
    print(f"[SOM] grid={grid_x}×{grid_y}, iterations={iterations}")
    n_features = embeddings.shape[1]
    som = MiniSom(grid_x, grid_y, n_features,
                  sigma=1.0, learning_rate=0.5,
                  random_seed=RANDOM_STATE)
    som.random_weights_init(embeddings)
    som.train(embeddings, iterations, verbose=False)

    labels = np.array([
        som.winner(e)[0] * grid_y + som.winner(e)[1]
        for e in embeddings
    ])
    return labels


def run_gmm(embeddings: np.ndarray,
            n_components: int = N_CLUSTERS) -> np.ndarray:
    """Gaussian Mixture Model."""
    from sklearn.mixture import GaussianMixture
    print(f"[GMM] n_components={n_components}")
    model = GaussianMixture(n_components=n_components,
                             random_state=RANDOM_STATE,
                             covariance_type="full",
                             max_iter=200)
    return model.fit_predict(embeddings)


def run_mean_shift(embeddings: np.ndarray,
                   bandwidth=MEAN_SHIFT_BW) -> np.ndarray:
    """Mean Shift clustering (bandwidth estimated if None)."""
    from sklearn.cluster import MeanShift, estimate_bandwidth
    if bandwidth is None:
        bandwidth = estimate_bandwidth(embeddings, quantile=0.2, n_samples=500)
        bandwidth = max(bandwidth, 0.1)   # guard against near-zero
    print(f"[Mean Shift] bandwidth={bandwidth:.4f}")
    model = MeanShift(bandwidth=bandwidth, bin_seeding=True, n_jobs=-1)
    return model.fit_predict(embeddings)


def run_bertopic(texts: list[str],
                 min_topic_size: int = BERTOPIC_MIN_TOPIC) -> tuple[np.ndarray, object]:
    """
    BERTopic with its own internal pipeline (UMAP + HDBSCAN).
    Returns (labels, fitted_model).
    """
    from bertopic import BERTopic
    print(f"[BERTopic] min_topic_size={min_topic_size}")
    topic_model = BERTopic(language="multilingual",
                           min_topic_size=min_topic_size,
                           verbose=False)
    topics, _ = topic_model.fit_transform(texts)
    return np.array(topics), topic_model


# =============================================================================
# 5. EVALUATION METRICS
# =============================================================================

def evaluate(embeddings: np.ndarray, labels: np.ndarray) -> dict:
    """
    Compute Silhouette Score and Davies-Bouldin Index.
    Noise points (label == -1) are excluded.
    """
    from sklearn.metrics import silhouette_score, davies_bouldin_score

    mask = labels != -1
    n_unique = len(set(labels[mask]))

    if n_unique < 2:
        return {"silhouette": np.nan,
                "davies_bouldin": np.nan,
                "n_clusters": n_unique,
                "n_noise": int((labels == -1).sum())}

    sil = silhouette_score(embeddings[mask], labels[mask], sample_size=min(5000, mask.sum()))
    db  = davies_bouldin_score(embeddings[mask], labels[mask])

    return {
        "silhouette":      round(float(sil), 4),
        "davies_bouldin":  round(float(db),  4),
        "n_clusters":      n_unique,
        "n_noise":         int((labels == -1).sum()),
    }


# =============================================================================
# 6. VISUALISATION
# =============================================================================

PALETTE = [
    "#E63946", "#457B9D", "#2A9D8F", "#E9C46A",
    "#F4A261", "#264653", "#6D6875", "#B5838D",
    "#ADBFC8", "#80B918", "#FF6B6B", "#4ECDC4",
    "#C7F2A4", "#FAD643", "#9B5DE5", "#F15BB5",
    "#00BBF9", "#00F5D4", "#FEE440", "#FB5607",
]


def _get_colors(labels: np.ndarray) -> list:
    unique = sorted(set(labels))
    cmap   = {lbl: ("#888888" if lbl == -1 else PALETTE[i % len(PALETTE)])
              for i, lbl in enumerate(unique)}
    return [cmap[l] for l in labels]


def plot_scatter(ax, coords_2d: np.ndarray, labels: np.ndarray,
                 title: str, metrics: dict):
    colors = _get_colors(labels)
    ax.scatter(coords_2d[:, 0], coords_2d[:, 1],
               c=colors, s=12, alpha=0.7, linewidths=0)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=6)
    info = (f"Clusters: {metrics['n_clusters']}  "
            f"Sil: {metrics['silhouette']:.3f}  "
            f"DB: {metrics['davies_bouldin']:.3f}")
    ax.set_xlabel(info, fontsize=8)
    ax.set_xticks([]); ax.set_yticks([])
    ax.spines[["top","right","left","bottom"]].set_visible(False)


def plot_all_results(coords_2d: np.ndarray,
                     results: dict,
                     save_path: Path = OUTPUT_DIR / "all_clusters.png"):
    names  = list(results.keys())
    n      = len(names)
    ncols  = 3
    nrows  = (n + ncols - 1) // ncols

    fig = plt.figure(figsize=(6 * ncols, 5 * nrows), facecolor="#0f0f0f")
    fig.suptitle("Clustering Algorithm Comparison",
                 fontsize=16, fontweight="bold", color="white", y=1.01)

    for idx, name in enumerate(names):
        ax = fig.add_subplot(nrows, ncols, idx + 1, facecolor="#1a1a1a")
        ax.tick_params(colors="white")
        plot_scatter(ax, coords_2d, results[name]["labels"], name,
                     results[name]["metrics"])
        ax.title.set_color("white")
        ax.xaxis.label.set_color("#aaaaaa")

    plt.tight_layout()
    fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[Plot] Saved → {save_path}")


def plot_metrics_comparison(results: dict,
                             save_path: Path = OUTPUT_DIR / "metrics_comparison.png"):
    names = list(results.keys())
    sil   = [results[n]["metrics"]["silhouette"]     for n in names]
    db    = [results[n]["metrics"]["davies_bouldin"] for n in names]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor="#0f0f0f")
    fig.suptitle("Evaluation Metrics Comparison",
                 fontsize=14, fontweight="bold", color="white")

    bar_kw = dict(edgecolor="#333", linewidth=0.5)

    # Silhouette (higher = better)
    ax = axes[0]
    ax.set_facecolor("#1a1a1a")
    bars = ax.bar(names, sil, color=PALETTE[:len(names)], **bar_kw)
    ax.set_title("Silhouette Score  (↑ higher = better)",
                 color="white", fontsize=11)
    ax.set_ylabel("Score", color="white")
    ax.tick_params(colors="white", axis="both")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#555")
    ax.set_ylim(min(0, min(v for v in sil if not np.isnan(v)) - 0.05),
                max(v for v in sil if not np.isnan(v)) + 0.1)
    for bar, val in zip(bars, sil):
        if not np.isnan(val):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=9, color="white")
    ax.set_xticklabels(names, rotation=20, ha="right")

    # Davies-Bouldin (lower = better)
    ax = axes[1]
    ax.set_facecolor("#1a1a1a")
    bars = ax.bar(names, db, color=PALETTE[:len(names)], **bar_kw)
    ax.set_title("Davies-Bouldin Index  (↓ lower = better)",
                 color="white", fontsize=11)
    ax.set_ylabel("Index", color="white")
    ax.tick_params(colors="white", axis="both")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#555")
    for bar, val in zip(bars, db):
        if not np.isnan(val):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=9, color="white")
    ax.set_xticklabels(names, rotation=20, ha="right")

    plt.tight_layout()
    fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[Plot] Saved → {save_path}")


# =============================================================================
# 7. BERTOPIC-SPECIFIC VISUALISATION
# =============================================================================

def save_bertopic_visuals(topic_model, output_dir: Path = OUTPUT_DIR):
    """Save BERTopic's built-in visualisations to HTML files."""
    try:
        fig = topic_model.visualize_topics()
        fig.write_html(str(output_dir / "bertopic_intertopic_distance.html"))
        print("[BERTopic] Saved intertopic distance map →",
              output_dir / "bertopic_intertopic_distance.html")
    except Exception as e:
        print(f"[BERTopic] visualize_topics failed: {e}")

    try:
        fig = topic_model.visualize_barchart(top_n_topics=8)
        fig.write_html(str(output_dir / "bertopic_barchart.html"))
        print("[BERTopic] Saved barchart →",
              output_dir / "bertopic_barchart.html")
    except Exception as e:
        print(f"[BERTopic] visualize_barchart failed: {e}")


# =============================================================================
# 8. SOM U-MATRIX VISUALISATION
# =============================================================================

def plot_som_umatrix(embeddings: np.ndarray,
                     grid_x: int = SOM_GRID_X,
                     grid_y: int = SOM_GRID_Y,
                     save_path: Path = OUTPUT_DIR / "som_umatrix.png"):
    from minisom import MiniSom
    n_features = embeddings.shape[1]
    som = MiniSom(grid_x, grid_y, n_features,
                  sigma=1.0, learning_rate=0.5,
                  random_seed=RANDOM_STATE)
    som.random_weights_init(embeddings)
    som.train(embeddings, SOM_ITERATIONS, verbose=False)

    u_matrix = np.zeros((grid_x, grid_y))
    weights   = som.get_weights()
    for i in range(grid_x):
        for j in range(grid_y):
            neighbours = []
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                ni, nj = i+dx, j+dy
                if 0 <= ni < grid_x and 0 <= nj < grid_y:
                    neighbours.append(weights[ni, nj])
            if neighbours:
                u_matrix[i, j] = np.mean([
                    np.linalg.norm(weights[i,j] - n) for n in neighbours
                ])

    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#0f0f0f")
    ax.set_facecolor("#1a1a1a")
    im = ax.imshow(u_matrix, cmap="viridis", interpolation="nearest")
    plt.colorbar(im, ax=ax, label="Distance")
    ax.set_title("SOM U-Matrix", color="white", fontsize=12, fontweight="bold")
    ax.tick_params(colors="white")
    fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[Plot] Saved → {save_path}")


# =============================================================================
# 9. RESULTS SUMMARY TABLE
# =============================================================================

def print_summary_table(results: dict):
    print("\n" + "="*72)
    print(f"{'Algorithm':<15} {'Clusters':>9} {'Noise':>7} "
          f"{'Silhouette':>12} {'Davies-Bouldin':>16}")
    print("-"*72)
    for name, r in results.items():
        m = r["metrics"]
        sil = f"{m['silhouette']:.4f}" if not np.isnan(m['silhouette']) else "  N/A"
        db  = f"{m['davies_bouldin']:.4f}" if not np.isnan(m['davies_bouldin']) else "  N/A"
        print(f"{name:<15} {m['n_clusters']:>9} {m['n_noise']:>7} "
              f"{sil:>12} {db:>16}")
    print("="*72)

    # Best algorithm per metric
    valid_sil = {n: r["metrics"]["silhouette"] for n, r in results.items()
                 if not np.isnan(r["metrics"]["silhouette"])}
    valid_db  = {n: r["metrics"]["davies_bouldin"] for n, r in results.items()
                 if not np.isnan(r["metrics"]["davies_bouldin"])}
    if valid_sil:
        best_sil = max(valid_sil, key=valid_sil.get)
        print(f"\n★  Best Silhouette Score  → {best_sil} ({valid_sil[best_sil]:.4f})")
    if valid_db:
        best_db  = min(valid_db, key=valid_db.get)
        print(f"★  Best Davies-Bouldin    → {best_db}  ({valid_db[best_db]:.4f})\n")


# =============================================================================
# 10. MAIN PIPELINE
# =============================================================================

def main(csv_path: str | None = None,
         text_column: str = "text"):
    """
    End-to-end pipeline.

    Parameters
    ----------
    csv_path    : Path to your CSV dataset. Pass None to use built-in sample.
    text_column : Column name containing tweet text.
    """
    
    # print(Path(csv_path).exists(), text_column, csv_path)  # sanity check for CLI args
    # return
    # ── Load data ─────────────────────────────────────────────────────────────
    if csv_path and Path(csv_path).exists():
        texts = load_tweets_from_csv(csv_path, text_column)
        print(f"[Data] Loaded {len(texts)} tweets from {csv_path}")
    else:
        texts = load_sample_tweets()
        print(f"[Data] Using built-in sample ({len(texts)} tweets)")

    print("Test print: ", texts[0][:10], "…")  # sanity check;
    # ── Embeddings ────────────────────────────────────────────────────────────
    embeddings = get_embeddings(texts)
    
    
    # BARU: Reduksi dimensi DULU sebelum clustering
    print("\n[Pre-process] Reducing dimensions for CLUSTERING with UMAP...")
    from umap import UMAP
    # Reduksi ke 5-10 dimensi agar fitur tetap kaya tapi tidak "noisy"
    reducer_for_clustering = UMAP(n_neighbors=15, n_components=5, metric='cosine', random_state=42)
    embeddings_reduced = reducer_for_clustering.fit_transform(embeddings)

    print("\n[Pipeline] Running clustering algorithms on REDUCED data …")
    
    from sklearn.neighbors import NearestNeighbors
    import matplotlib.pyplot as plt

    def find_optimal_eps(embeddings):
        print("[DBSCAN] Calculating K-Distance Graph...")
        neigh = NearestNeighbors(n_neighbors=15)
        nbrs = neigh.fit(embeddings)
        distances, indices = nbrs.kneighbors(embeddings)
        distances = np.sort(distances[:, 14], axis=0)
        
        plt.figure(figsize=(10, 6))
        plt.plot(distances)
        plt.axhline(y=0.5, color='r', linestyle='--', label='Default EPS') # Garis bantu
        plt.title("K-Distance Graph - Cari titik 'Elbow'")
        plt.xlabel("Points sorted by distance")
        plt.ylabel("15th Nearest Neighbor Distance")
        plt.grid(True)
        
        # Simpan ke folder hasil agar bisa dicek nanti
        save_path = OUTPUT_DIR / "k_distance_elbow.png"
        plt.savefig(save_path)
        print(f"[DBSCAN] K-Distance plot saved to {save_path}")
        plt.close()
        
        
    # find_optimal_eps(embeddings_reduced)
    # return

    # ── Run all clustering algorithms ─────────────────────────────────────────
    print("\n[Pipeline] Running clustering algorithms new …")

    labels_kmeans     = run_kmeans(embeddings_reduced)
    labels_dbscan     = run_dbscan(embeddings_reduced)
    labels_som        = run_som(embeddings_reduced)
    labels_gmm        = run_gmm(embeddings_reduced)
    labels_meanshift  = run_mean_shift(embeddings_reduced)
    labels_bertopic, bertopic_model = run_bertopic(texts)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    print("\n[Evaluation] Computing metrics …")
    results = {
        "K-Means":    {"labels": labels_kmeans,    "metrics": evaluate(embeddings, labels_kmeans)},
        "DBSCAN":     {"labels": labels_dbscan,    "metrics": evaluate(embeddings, labels_dbscan)},
        "SOM":        {"labels": labels_som,        "metrics": evaluate(embeddings, labels_som)},
        "GMM":        {"labels": labels_gmm,        "metrics": evaluate(embeddings, labels_gmm)},
        "Mean Shift": {"labels": labels_meanshift,  "metrics": evaluate(embeddings, labels_meanshift)},
        "BERTopic":   {"labels": labels_bertopic,   "metrics": evaluate(embeddings, labels_bertopic)},
    }

    print_summary_table(results)

    # ── Dimensionality reduction for visualisation ────────────────────────────
    print("\n[Visualisation] Reducing dimensions for scatter plots …")
    coords_2d = reduce_dimensions(embeddings, method="umap", n_components=2)

    # For BERTopic, compute coords from texts embedding already done above
    # We reuse the same UMAP projection for all algorithms (fair comparison)

    # ── Scatter plots ─────────────────────────────────────────────────────────
    plot_all_results(coords_2d, results)
    plot_metrics_comparison(results)

    # ── BERTopic-specific HTML visuals ────────────────────────────────────────
    save_bertopic_visuals(bertopic_model)

    # ── SOM U-Matrix ─────────────────────────────────────────────────────────
    plot_som_umatrix(embeddings)

    # ── Save individual scatter plots ─────────────────────────────────────────
    for name, r in results.items():
        fig, ax = plt.subplots(figsize=(7, 6), facecolor="#0f0f0f")
        ax.set_facecolor("#1a1a1a")
        plot_scatter(ax, coords_2d, r["labels"], name, r["metrics"])
        ax.title.set_color("white")
        ax.xaxis.label.set_color("#aaaaaa")
        fname = OUTPUT_DIR / f"cluster_{name.lower().replace(' ','_')}.png"
        fig.savefig(fname, dpi=FIGURE_DPI, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)

    # ── Save metrics CSV ─────────────────────────────────────────────────────
    rows = []
    for name, r in results.items():
        row = {"algorithm": name, **r["metrics"]}
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "metrics_summary.csv", index=False)
    print(f"\n[Done] All outputs saved in ./{OUTPUT_DIR}/")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare 6 clustering algorithms on tweet embeddings."
    )
    parser.add_argument("--csv",    default=None,   help="Path to CSV dataset file")
    parser.add_argument("--col",    default="text", help="Text column name (default: 'text')")
    parser.add_argument("--k",      default=N_CLUSTERS,    type=int,   help="Number of clusters (K-Means, GMM, SOM)")
    parser.add_argument("--eps",    default=DBSCAN_EPS,    type=float, help="DBSCAN eps")
    parser.add_argument("--minsam", default=DBSCAN_MIN_SAMPLES, type=int, help="DBSCAN min_samples")

    args = parser.parse_args()

    # Override globals with CLI args
    N_CLUSTERS           = args.k
    DBSCAN_EPS           = args.eps
    DBSCAN_MIN_SAMPLES   = args.minsam

    main(csv_path=args.csv, text_column=args.col)
