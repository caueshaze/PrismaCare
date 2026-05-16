import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme/colors';
import { api } from '../services/api';
import { DoseReminderInput, syncDoseReminders } from '../services/notificationService';

type Dose = DoseReminderInput & {
  confirmacao_id: number;
  horario_previsto: string;
  horario_confirmacao: string | null;
  status: 'PENDENTE' | 'CONFIRMADO' | 'ATRASADO' | 'CANCELADO' | 'NAO_CONFIRMADO';
  medicamento: { nome: string; dosagem: string; observacao?: string };
};

const STATUS_CONFIG = {
  PENDENTE:       { label: 'Pendente',       color: '#F59E0B', bg: '#FEF3C7' },
  CONFIRMADO:     { label: 'Confirmado',     color: '#10B981', bg: '#D1FAE5' },
  ATRASADO:       { label: 'Atrasado',       color: '#EF4444', bg: '#FEE2E2' },
  CANCELADO:      { label: 'Cancelado',      color: '#6B7280', bg: '#F3F4F6' },
  NAO_CONFIRMADO: { label: 'Não Confirmado', color: '#7F1D1D', bg: '#FEE2E2' }, // Tom vermelho escuro/vencido
};

export default function DosesScreen() {
  const [doses, setDoses] = useState<Dose[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState<number | null>(null);

  const buscar = useCallback(async () => {
    try {
      const data = await api<Dose[]>('/api/doses/hoje');
      setDoses(data);
      await syncDoseReminders(data);
    } catch (e: any) {
      Alert.alert('Erro', e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { buscar(); }, [buscar]);

  async function confirmar(id: number) {
    setConfirming(id);
    try {
      await api(`/api/confirmacoes/${id}/confirmar`, { method: 'PUT' });
      await buscar();
    } catch (e: any) {
      Alert.alert('Erro', e.message);
    } finally {
      setConfirming(null);
    }
  }

  if (loading) return <ActivityIndicator style={styles.center} color={colors.primary} size="large" />;

  return (
    <View style={styles.container}>
      <FlatList
        data={doses}
        keyExtractor={(item) => String(item.confirmacao_id)}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>Nenhuma dose programada para hoje.</Text>}
        renderItem={({ item }) => {
          const cfg = STATUS_CONFIG[item.status] ?? STATUS_CONFIG.PENDENTE;
          return (
            <View style={styles.card}>
              <View style={styles.cardTop}>
                <View style={styles.medInfo}>
                  <Text style={styles.medNome}>{item.medicamento.nome}</Text>
                  <Text style={styles.medDosagem}>{item.medicamento.dosagem}</Text>
                </View>
                <View style={[styles.badge, { backgroundColor: cfg.bg }]}>
                  <Text style={[styles.badgeText, { color: cfg.color }]}>{cfg.label}</Text>
                </View>
              </View>

              <View style={styles.timeRow}>
                <Ionicons name="time-outline" size={14} color={colors.textMuted} />
                <Text style={styles.timeText}>
                  Previsto: {item.horario_previsto?.substring(11, 16) ?? '—'}
                </Text>
                {item.horario_confirmacao ? (
                  <Text style={styles.timeText}>
                    {'  '}Confirmado: {item.horario_confirmacao?.substring(11, 16)}
                  </Text>
                ) : null}
              </View>

              {item.status === 'PENDENTE' && (
                <TouchableOpacity
                  style={styles.confirmBtn}
                  onPress={() => confirmar(item.confirmacao_id)}
                  disabled={confirming === item.confirmacao_id}
                >
                  {confirming === item.confirmacao_id ? (
                    <ActivityIndicator color={colors.white} size="small" />
                  ) : (
                    <>
                      <Ionicons name="checkmark-circle-outline" size={18} color={colors.white} />
                      <Text style={styles.confirmText}>Confirmar tomada</Text>
                    </>
                  )}
                </TouchableOpacity>
              )}
            </View>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  list: { padding: 16 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 40, fontSize: 14 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 8,
    elevation: 2,
  },
  cardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  medInfo: { flex: 1 },
  medNome: { fontSize: 15, fontWeight: '700', color: colors.textPrimary },
  medDosagem: { fontSize: 13, color: colors.textSecondary, marginTop: 2 },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
    marginLeft: 8,
  },
  badgeText: { fontSize: 11, fontWeight: '700' },
  timeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    gap: 4,
  },
  timeText: { fontSize: 12, color: colors.textMuted },
  confirmBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    marginTop: 12,
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 10,
  },
  confirmText: { color: colors.white, fontWeight: '700', fontSize: 14 },
});
