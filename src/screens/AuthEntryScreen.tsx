import React, { useContext, useEffect, useRef, useState } from 'react';
import {
  Alert,
  Animated,
  Easing,
  Image,
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  TouchableWithoutFeedback,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { colors } from '../theme/colors';
import InputField from '../components/InputField';
import PrimaryButton from '../components/PrimaryButton';
import { AuthContext } from '../contexts/AuthContext';
import { lookupEmail, registerRequest } from '../services/api';
import { RootStackParamList } from '../../App';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'AuthEntry'>;
};

type Step = 'email' | 'existingPassword' | 'newPassword';

function validateEmail(email: string): boolean {
  return /\S+@\S+\.\S+/.test(email.trim());
}

function isPhoneCandidate(value: string): boolean {
  return value.replace(/\D/g, '').length >= 8;
}

export default function AuthEntryScreen({ navigation }: Props) {
  const { signIn } = useContext(AuthContext);
  const [step, setStep] = useState<Step>('email');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();

  const normalizedEmail = email.trim().toLowerCase();
  const isExisting = step === 'existingPassword';
  const isNew = step === 'newPassword';
  const entrance = useRef(new Animated.Value(0)).current;
  const stepProgress = useRef(new Animated.Value(1)).current;
  const pulse = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(entrance, {
      toValue: 1,
      duration: 620,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();

    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, {
          toValue: 1,
          duration: 1900,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: true,
        }),
        Animated.timing(pulse, {
          toValue: 0,
          duration: 1900,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: true,
        }),
      ]),
    );
    loop.start();

    return () => loop.stop();
  }, [entrance, pulse]);

  useEffect(() => {
    stepProgress.setValue(0);
    Animated.timing(stepProgress, {
      toValue: 1,
      duration: 280,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }).start();
  }, [step, stepProgress]);

  async function handleEmail() {
    if (isPhoneCandidate(email)) {
      setError('Login com número será habilitado em breve. Por enquanto, entre com seu e-mail e senha.');
      return;
    }

    if (!validateEmail(email)) {
      setError('Informe um número ou e-mail válido.');
      return;
    }

    setLoading(true);
    setError(undefined);
    try {
      const result = await lookupEmail(normalizedEmail);
      setPassword('');
      setStep(result.exists ? 'existingPassword' : 'newPassword');
    } catch (e: any) {
      Alert.alert('Não foi possível continuar', e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handlePassword() {
    if (password.length < 6) {
      setError('Senha deve ter pelo menos 6 caracteres.');
      return;
    }

    setLoading(true);
    setError(undefined);
    try {
      if (isNew) {
        await registerRequest(normalizedEmail, password);
      }
      await signIn(normalizedEmail, password);
    } catch (e: any) {
      Alert.alert(isNew ? 'Erro ao criar conta' : 'Erro ao entrar', e.message);
    } finally {
      setLoading(false);
    }
  }

  function goBackToEmail() {
    setStep('email');
    setPassword('');
    setError(undefined);
  }

  const title = step === 'email'
    ? 'Inicie com seu número ou e-mail'
    : isExisting
      ? 'Bem-vindo de volta!'
      : 'Crie uma senha';

  const subtitle = step === 'email'
    ? 'Use seu e-mail para entrar hoje. O acesso por número será liberado em breve.'
    : normalizedEmail;

  const entranceStyle = {
    opacity: entrance,
    transform: [
      {
        translateY: entrance.interpolate({
          inputRange: [0, 1],
          outputRange: [18, 0],
        }),
      },
    ],
  };

  const stepStyle = {
    opacity: stepProgress,
    transform: [
      {
        translateY: stepProgress.interpolate({
          inputRange: [0, 1],
          outputRange: [12, 0],
        }),
      },
    ],
  };

  const pulseScale = pulse.interpolate({
    inputRange: [0, 1],
    outputRange: [1, 1.025],
  });

  const logoEntranceStyle = {
    opacity: entrance,
    transform: [
      {
        translateY: entrance.interpolate({
          inputRange: [0, 1],
          outputRange: [18, 0],
        }),
      },
      { scale: pulseScale },
    ],
  };

  return (
    <View style={styles.flex}>
      <LinearGradient
        colors={[colors.gradientStart, colors.gradientMid, colors.gradientEnd]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.header}
      />
      <Animated.View style={[styles.glow, styles.glowTop, { transform: [{ scale: pulseScale }] }]} />
      <Animated.View style={[styles.glow, styles.glowSide, { transform: [{ scale: pulseScale }] }]} />

      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <ScrollView
            contentContainerStyle={styles.scroll}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <Animated.View style={[styles.logoBadge, logoEntranceStyle]}>
              <Image source={require('../../assets/logo.png')} style={styles.logoImage} resizeMode="contain" />
            </Animated.View>

            <Animated.View style={[styles.card, entranceStyle]}>
              {step !== 'email' && (
                <TouchableOpacity style={styles.backButton} onPress={goBackToEmail}>
                  <Ionicons name="arrow-back" size={18} color={colors.primary} />
                  <Text style={styles.backText}>Trocar e-mail</Text>
                </TouchableOpacity>
              )}

              <Animated.View style={stepStyle}>
                <Text style={styles.title}>{title}</Text>
                {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}

                {step === 'email' ? (
                  <InputField
                    label="Número ou e-mail"
                    iconName="person-outline"
                    placeholder="Seu número ou e-mail"
                    value={email}
                    onChangeText={(value) => {
                      setEmail(value);
                      setError(undefined);
                    }}
                    keyboardType="default"
                    autoCapitalize="none"
                    autoCorrect={false}
                    error={error}
                  />
                ) : (
                  <>
                    <InputField
                      label="Senha"
                      iconName="lock-closed-outline"
                      placeholder={isExisting ? 'Digite sua senha' : 'Mínimo 6 caracteres'}
                      value={password}
                      onChangeText={(value) => {
                        setPassword(value);
                        setError(undefined);
                      }}
                      isPassword
                      error={error}
                    />
                    {isExisting && (
                      <TouchableOpacity
                        style={styles.forgotButton}
                        onPress={() => navigation.navigate('ForgotPassword')}
                      >
                        <Text style={styles.forgotText}>Esqueci minha senha</Text>
                      </TouchableOpacity>
                    )}
                  </>
                )}

                <PrimaryButton
                  title={step === 'email' ? 'Continuar' : isExisting ? 'Entrar' : 'Criar conta'}
                  onPress={step === 'email' ? handleEmail : handlePassword}
                  loading={loading}
                  iconName={step === 'email' ? 'arrow-forward' : 'checkmark'}
                  style={styles.primaryButton}
                />

                {step === 'email' ? (
                  <>
                    <View style={styles.dividerRow}>
                      <View style={styles.dividerLine} />
                      <Text style={styles.dividerText}>ou continue com</Text>
                      <View style={styles.dividerLine} />
                    </View>

                    <View style={styles.socialDisabledBtn}>
                      <Ionicons name="logo-google" size={20} color={colors.textSecondary} />
                      <Text style={styles.socialDisabledText}>Google em breve</Text>
                    </View>
                  </>
                ) : null}
              </Animated.View>
            </Animated.View>
          </ScrollView>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  header: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 260,
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
  },
  glow: {
    position: 'absolute',
    borderRadius: 999,
    backgroundColor: 'rgba(255,255,255,0.18)',
  },
  glowTop: {
    width: 210,
    height: 210,
    top: -52,
    right: -48,
  },
  glowSide: {
    width: 150,
    height: 150,
    top: 126,
    left: -50,
    backgroundColor: 'rgba(255,255,255,0.13)',
  },
  scroll: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 72,
    paddingBottom: 32,
  },
  logoBadge: {
    alignSelf: 'center',
    width: 120,
    height: 120,
    borderRadius: 30,
    backgroundColor: colors.white,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 28,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.18,
    shadowRadius: 18,
    elevation: 8,
  },
  logoImage: { width: '82%', height: '82%' },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 24,
    padding: 24,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 18,
    elevation: 6,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    gap: 6,
    marginBottom: 18,
  },
  backText: { color: colors.primary, fontWeight: '700', fontSize: 13 },
  title: {
    fontSize: 24,
    lineHeight: 30,
    fontWeight: '800',
    color: colors.textPrimary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.textSecondary,
    marginBottom: 24,
  },
  forgotButton: {
    alignSelf: 'flex-end',
    marginTop: -4,
    marginBottom: 18,
  },
  forgotText: { color: colors.primary, fontWeight: '700' },
  primaryButton: { marginTop: 4 },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 22,
    marginBottom: 16,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: colors.border,
  },
  dividerText: {
    marginHorizontal: 12,
    fontSize: 11,
    color: colors.textMuted,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  socialDisabledBtn: {
    minHeight: 52,
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    opacity: 0.9,
  },
  socialDisabledText: {
    fontSize: 14,
    color: colors.textSecondary,
    fontWeight: '700',
  },
});
