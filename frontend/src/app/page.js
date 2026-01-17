'use client';

import styles from './page.module.css';
import PredictionForm from '../components/PredictionForm';

export default function Home() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.logo}>🎗️</div>
        <h1 className={styles.title}>Bağış Potansiyeli Tahmini</h1>
        <p className={styles.subtitle}>Türk Kanser Derneği için şirket analizi</p>
      </header>

      <PredictionForm />

      <footer className={styles.footer}>
        Model 272 global şirket verisiyle eğitildi • TKD Smart Classifier
      </footer>
    </div>
  );
}
