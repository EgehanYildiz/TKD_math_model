import { useState } from 'react';
import styles from '../app/page.module.css';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5328';

const SEKTORLER = [
    { value: 'RETAIL_CONSUMER', label: 'Perakende / Tüketici' },
    { value: 'PHARMA_HEALTH', label: 'Sağlık / İlaç' },
    { value: 'ENERGY_UTILITIES', label: 'Enerji' },
    { value: 'FINANCE_INSURANCE', label: 'Finans / Sigorta' },
    { value: 'TECH_TELECOM', label: 'Teknoloji' },
    { value: 'MANUFACTURING', label: 'Üretim / Sanayi' },
    { value: 'SERVICES_OTHER', label: 'Hizmet / Diğer' },
];

const SEVIYELER = {
    1: {
        isim: 'Çok Düşük Potansiyel',
        aciklama: 'Giriş seviyesi. Bu kurumla standart bağış veya tek seferlik proje işbirlikleri hedeflenmelidir. Kabul etme olasılıkları düşüktür.'
    },
    2: {
        isim: 'Düşük Potansiyel',
        aciklama: 'Gelişime açık. Bu kurumla proje bazlı, dönemsel veya çalışan gönüllülüğü içeren işbirlikleri hedeflenmelidir. Kabul etme olasılıkları düşüktür.'
    },
    3: {
        isim: 'Orta Potansiyel',
        aciklama: 'İdeal büyüme alanı. Bu kurumla yıllık, sürdürülebilir ve orta ölçekli sponsorluklar hedeflenmelidir. Kabul etme olasılıkları orta seviyedir, doğru mesaj ve iletişimle artabilir.'
    },
    4: {
        isim: 'Yüksek Potansiyel',
        aciklama: 'Stratejik ortak. Bu kurumla uzun vadeli, yüksek hacimli ve çok yönlü işbirlikleri mümkündür. Kabul etme olasılıkları yüksek seviyedir, doğru mesaj ve iletişimle artabilir.'
    },
    5: {
        isim: 'Çok Yüksek Potansiyel',
        aciklama: 'Vizyoner Lider. Bu kurumla en üst düzey, çok paydaşlı ve dönüştürücü stratejik ortaklıklar kurulmalıdır. Kabul etme olasılıkları çok yüksek seviyedir, doğru mesaj ve iletişimle artabilir.'
    },
};

export default function PredictionForm() {
    const [form, setForm] = useState({
        sektor: 'RETAIL_CONSUMER',
        calisanSayisi: 1000,
        yil: 20,
        halkaAcik: false,
        b2c: true,
        esg: false,
        sube: false,
        ungc: false,
    });

    const [sonuc, setSonuc] = useState(null);
    const [yukleniyor, setYukleniyor] = useState(false);
    const [hata, setHata] = useState(null);

    const degistir = (alan, deger) => {
        setForm(prev => ({ ...prev, [alan]: deger }));
    };

    const gonder = async (e) => {
        e.preventDefault();
        setYukleniyor(true);
        setHata(null);
        setSonuc(null);

        try {
            const response = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    industry_type: form.sektor,
                    business_type: form.b2c ? 1 : 0,
                    esg_content: form.esg ? 1 : 0,
                    employee_count: form.calisanSayisi,
                    publicly_traded: form.halkaAcik ? 1 : 0,
                    years_active: form.yil,
                    is_subsidiary: form.sube ? 1 : 0,
                    un_global: form.ungc ? 1 : 0,
                }),
            });

            if (!response.ok) throw new Error('Bağlantı hatası');
            const data = await response.json();
            setSonuc(data);
        } catch (err) {
            setHata('Tahmin yapılamadı. API çalışmıyor olabilir.');
        } finally {
            setYukleniyor(false);
        }
    };

    return (
        <>
            <div className={styles.card}>
                <h2 className={styles.cardTitle}>Şirket Bilgileri</h2>

                <form onSubmit={gonder}>
                    <div className={styles.formGroup}>
                        <label className={styles.label}>Sektör</label>
                        <select
                            className={styles.select}
                            value={form.sektor}
                            onChange={(e) => degistir('sektor', e.target.value)}
                        >
                            {SEKTORLER.map(s => (
                                <option key={s.value} value={s.value}>{s.label}</option>
                            ))}
                        </select>
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>Çalışan Sayısı</label>
                        <input
                            type="number"
                            className={styles.input}
                            value={form.calisanSayisi}
                            onChange={(e) => degistir('calisanSayisi', Number(e.target.value))}
                            min="1"
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>Kuruluş Yılı (Kaç yıldır aktif)</label>
                        <input
                            type="number"
                            className={styles.input}
                            value={form.yil}
                            onChange={(e) => degistir('yil', Number(e.target.value))}
                            min="1"
                        />
                    </div>

                    <div style={{ marginTop: '1rem' }}>
                        <div className={styles.toggleRow}>
                            <span className={styles.toggleLabel}>Tüketiciye satış yapıyor (B2C)</span>
                            <div
                                className={`${styles.toggle} ${form.b2c ? styles.active : ''}`}
                                onClick={() => degistir('b2c', !form.b2c)}
                            />
                        </div>

                        <div className={styles.toggleRow}>
                            <span className={styles.toggleLabel}>Halka açık şirket (Borsa)</span>
                            <div
                                className={`${styles.toggle} ${form.halkaAcik ? styles.active : ''}`}
                                onClick={() => degistir('halkaAcik', !form.halkaAcik)}
                            />
                        </div>

                        <div className={styles.toggleRow}>
                            <span className={styles.toggleLabel}>Sürdürülebilirlik raporu var</span>
                            <div
                                className={`${styles.toggle} ${form.esg ? styles.active : ''}`}
                                onClick={() => degistir('esg', !form.esg)}
                            />
                        </div>

                        <div className={styles.toggleRow}>
                            <span className={styles.toggleLabel}>Global şirketin Türkiye şubesi</span>
                            <div
                                className={`${styles.toggle} ${form.sube ? styles.active : ''}`}
                                onClick={() => degistir('sube', !form.sube)}
                            />
                        </div>

                        <div className={styles.toggleRow}>
                            <span className={styles.toggleLabel}>UN Global Compact üyesi</span>
                            <div
                                className={`${styles.toggle} ${form.ungc ? styles.active : ''}`}
                                onClick={() => degistir('ungc', !form.ungc)}
                            />
                        </div>
                    </div>

                    <button type="submit" className={styles.button} disabled={yukleniyor}>
                        {yukleniyor ? 'Analiz ediliyor...' : 'Potansiyeli Hesapla'}
                    </button>
                </form>
            </div>

            {/* Sonuç */}
            <div className={styles.card}>
                <h2 className={styles.cardTitle}>Sonuç</h2>

                {yukleniyor && (
                    <div className={styles.loading}>
                        <div className={styles.spinner}></div>
                        <p>Yapay zeka analiz yapıyor...</p>
                    </div>
                )}

                {hata && <div className={styles.error}>{hata}</div>}

                {sonuc && !yukleniyor && (
                    <div className={styles.resultBox}>
                        <div className={styles.tierName}>
                            {SEVIYELER[sonuc.tier_code]?.isim}
                        </div>
                        <div className={styles.tierDesc} style={{ fontStyle: 'italic', color: '#64748b', marginTop: '0.5rem' }}>
                            {SEVIYELER[sonuc.tier_code]?.aciklama}
                        </div>

                        <div className={styles.accuracy}>
                            Güven Skoru: %{(sonuc.confidence * 100).toFixed(1)}
                        </div>

                        {/* Top-2 Stratejik Öneri */}
                        {(() => {
                            // Find indices of top 2
                            const probsWithIndex = sonuc.probabilities.map((p, i) => ({ prob: p, idx: i + 1 }));
                            probsWithIndex.sort((a, b) => b.prob - a.prob);
                            const top1 = probsWithIndex[0];
                            const top2 = probsWithIndex[1];
                            const combinedConf = (top1.prob + top2.prob) * 100;

                            // Recommendation: Higher Probability Class (User Correction)
                            const rec = top1;
                            const recName = SEVIYELER[rec.idx].isim;

                            return (
                                <div style={{
                                    backgroundColor: '#f0f9ff',
                                    border: '1px solid #bae6fd',
                                    borderRadius: '8px',
                                    padding: '1rem',
                                    margin: '1rem 0',
                                    fontSize: '0.9rem',
                                    color: '#0c4a6e'
                                }}>
                                    <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#0284c7' }}>
                                        💡 Stratejik Öneri (Top-2 Yaklaşımı)
                                    </strong>
                                    Yapay zeka ilk 2 tahminde <strong>%80'e yakın doğruluk</strong> oranına sahiptir.
                                    <br /><br />
                                    Bu şirketin gerçek potansiyeli büyük ihtimalle <strong>{SEVIYELER[top1.idx].isim}</strong> veya <strong>{SEVIYELER[top2.idx].isim}</strong> seviyesindedir (Toplam İhtimal: %{combinedConf.toFixed(0)}).
                                    <br /><br />
                                    İnsan yorumunu ve bilgisayar içgörüsünü beraber hesaba katarak, top-2 sınıflandırmadan hangisinin seçmek istediğinize kendiniz karar vermeniz tavsiye edilir.
                                </div>
                            );
                        })()}

                        <div className={styles.probContainer}>
                            {/* 1: Believe, 2: Inspire, 3: Dream, 4: Hope, 5: Vision */}
                            {sonuc.probabilities.map((prob, idx) => {
                                const level = idx + 1;
                                const name = SEVIYELER[level]?.isim;
                                const percent = (prob * 100).toFixed(1);

                                // Highlight top 2
                                const probsWithIndex = sonuc.probabilities.map((p, i) => ({ prob: p, idx: i + 1 }));
                                probsWithIndex.sort((a, b) => b.prob - a.prob);
                                const isTop2 = level === probsWithIndex[0].idx || level === probsWithIndex[1].idx;

                                return (
                                    <div key={level} className={styles.probRow} style={{ opacity: isTop2 ? 1 : 0.5 }}>
                                        <div className={styles.probHeader}>
                                            <span className={styles.probLabel} style={{ fontWeight: isTop2 ? 'bold' : 'normal' }}>
                                                {name} {isTop2 && '⭐'}
                                            </span>
                                            <span className={styles.probValue}>%{percent}</span>
                                        </div>
                                        <div className={styles.probBarBg}>
                                            <div
                                                className={styles.probBarFill}
                                                style={{
                                                    width: `${percent}%`,
                                                    backgroundColor: isTop2 ? '#2563eb' : '#94a3b8'
                                                }}
                                            />
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}
