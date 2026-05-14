import 'react-native-gesture-handler';
import React, { useContext } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { colors } from './src/theme/colors';
import { AuthProvider, AuthContext } from './src/contexts/AuthContext';

import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import ForgotPasswordScreen from './src/screens/ForgotPasswordScreen';
import HomeScreen from './src/screens/HomeScreen';
import MedicamentosScreen from './src/screens/MedicamentosScreen';
import AgendamentosScreen from './src/screens/AgendamentosScreen';
import ContatosScreen from './src/screens/ContatosScreen';
import DosesScreen from './src/screens/DosesScreen';

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
  Home: undefined;
  Medicamentos: undefined;
  Agendamentos: undefined;
  Contatos: undefined;
  Doses: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

const screenOptions = {
  headerStyle: { backgroundColor: colors.background },
  headerTintColor: colors.primary,
  headerTitleStyle: { fontWeight: '700' as const },
  headerShadowVisible: false,
  contentStyle: { backgroundColor: colors.background },
};

function Navigation() {
  const { token } = useContext(AuthContext);

  return (
    <Stack.Navigator screenOptions={screenOptions}>
      {token == null ? (
        <>
          <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
          <Stack.Screen name="Register" component={RegisterScreen} options={{ title: 'Criar Conta' }} />
          <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} options={{ title: 'Redefinir Senha' }} />
        </>
      ) : (
        <>
          <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
          <Stack.Screen name="Medicamentos" component={MedicamentosScreen} options={{ title: 'Medicamentos' }} />
          <Stack.Screen name="Agendamentos" component={AgendamentosScreen} options={{ title: 'Agendamentos' }} />
          <Stack.Screen name="Contatos" component={ContatosScreen} options={{ title: 'Contatos' }} />
          <Stack.Screen name="Doses" component={DosesScreen} options={{ title: 'Doses de Hoje' }} />
        </>
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <StatusBar style="light" translucent />
        <Navigation />
      </NavigationContainer>
    </AuthProvider>
  );
}
