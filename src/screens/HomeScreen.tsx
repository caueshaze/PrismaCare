import React, { useContext } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors } from '../theme/colors';
import { AuthContext } from '../contexts/AuthContext';
import { RootStackParamList } from '../../App';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Home'>;
};

type MenuItem = {
  title: string;
  subtitle: string;
  icon: keyof typeof Ionicons.glyphMap;
  screen: keyof RootStackParamList;
  color: string;
};

const MENU: MenuItem[] = [
  { title: 'Medicamentos', subtitle: 'Cadastrar e listar', icon: 'medkit-outline', screen: 'Medicamentos', color: '#5BAD8F' },
  { title: 'Agendamentos', subtitle: 'Horários e doses', icon: 'calendar-outline', screen: 'Agendamentos', color: '#7DD3AE' },
  { title: 'Contatos', subtitle: 'Emergência e cuidadores', icon: 'people-outline', screen: 'Contatos', color: '#3D8B6E' },
  { title: 'Doses de Hoje', subtitle: 'Confirmar tomadas', icon: 'checkmark-circle-outline', screen: 'Doses', color: '#2A6B52' },
];

export default function HomeScreen({ navigation }: Props) {
  const { signOut } = useContext(AuthContext);

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={[colors.gradientStart, colors.gradientMid, colors.gradientEnd]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.header}
      >
        <SafeAreaView>
          <View style={styles.headerRow}>
            <View>
              <Text style={styles.greeting}>PrismaCare</Text>
              <Text style={styles.greetingSub}>O que você quer fazer?</Text>
            </View>
            <TouchableOpacity style={styles.logoutBtn} onPress={signOut}>
              <Ionicons name="log-out-outline" size={22} color={colors.white} />
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </LinearGradient>

      <View style={styles.grid}>
        {MENU.map((item) => (
          <TouchableOpacity
            key={item.screen}
            style={styles.card}
            activeOpacity={0.8}
            onPress={() => navigation.navigate(item.screen as any)}
          >
            <View style={[styles.iconCircle, { backgroundColor: item.color + '20' }]}>
              <Ionicons name={item.icon} size={28} color={item.color} />
            </View>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.cardSub}>{item.subtitle}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: {
    paddingTop: (StatusBar.currentHeight ?? 0) + 16,
    paddingBottom: 28,
    paddingHorizontal: 24,
    borderBottomLeftRadius: 28,
    borderBottomRightRadius: 28,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  greeting: { fontSize: 22, fontWeight: '800', color: colors.white },
  greetingSub: { fontSize: 14, color: 'rgba(255,255,255,0.8)', marginTop: 2 },
  logoutBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  card: {
    width: '47%',
    backgroundColor: colors.surface,
    borderRadius: 20,
    padding: 20,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
  },
  iconCircle: {
    width: 52,
    height: 52,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  cardTitle: { fontSize: 15, fontWeight: '700', color: colors.textPrimary },
  cardSub: { fontSize: 12, color: colors.textMuted, marginTop: 4 },
});
