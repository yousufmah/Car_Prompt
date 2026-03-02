"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Car, Eye, EyeOff, Lock, Mail, Building, Chrome, Github, Square, Phone, MapPin, User, Check } from "lucide-react";

type FormMode = "login" | "register";

interface RegistrationData {
  garageName: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone: string;
  address: string;
  contactName: string;
}

export default function GarageLogin() {
  const [mode, setMode] = useState<FormMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [registrationData, setRegistrationData] = useState<RegistrationData>({
    garageName: "",
    email: "",
    password: "",
    confirmPassword: "",
    phone: "",
    address: "",
    contactName: "",
  });
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [passwordCriteria, setPasswordCriteria] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false,
  });
  const router = useRouter();

  // Calculate password strength and criteria
  useEffect(() => {
    if (!password) {
      setPasswordStrength(0);
      setPasswordCriteria({
        length: false,
        uppercase: false,
        lowercase: false,
        number: false,
        special: false,
      });
      return;
    }
    
    let score = 0;
    // Length
    const hasLength = password.length >= 8;
    const hasLongLength = password.length >= 12;
    if (hasLength) score += 25;
    if (hasLongLength) score += 15;
    
    // Character variety
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[^A-Za-z0-9]/.test(password);
    
    if (hasUppercase) score += 20;
    if (hasLowercase) score += 20;
    if (hasNumber) score += 20;
    if (hasSpecial) score += 20;
    
    // Cap at 100
    setPasswordStrength(Math.min(score, 100));
    setPasswordCriteria({
      length: hasLength,
      uppercase: hasUppercase,
      lowercase: hasLowercase,
      number: hasNumber,
      special: hasSpecial,
    });
  }, [password]);

  const getStrengthColor = () => {
    if (passwordStrength < 30) return "bg-red-500";
    if (passwordStrength < 60) return "bg-yellow-500";
    if (passwordStrength < 80) return "bg-blue-500";
    return "bg-green-500";
  };

  const getStrengthLabel = () => {
    if (passwordStrength < 30) return "Weak";
    if (passwordStrength < 60) return "Fair";
    if (passwordStrength < 80) return "Good";
    return "Strong";
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Redirect to garage analytics
    router.push("/garage/analytics");
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate passwords match
    if (registrationData.password !== registrationData.confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    
    // Validate password strength
    if (passwordStrength < 60) {
      alert("Please use a stronger password (at least 'Good' strength)");
      return;
    }
    
    setIsLoading(true);
    
    // Simulate registration API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    alert("Registration submitted! You'll be contacted for verification.");
    setMode("login");
    setIsLoading(false);
  };

  const handleOAuth = (provider: string) => {
    alert(`OAuth with ${provider} would be implemented here`);
  };

  const handleRegistrationChange = (field: keyof RegistrationData, value: string) => {
    setRegistrationData(prev => ({ ...prev, [field]: value }));
    // Update password field for strength calculation
    if (field === "password") {
      setPassword(value);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-blue-600/20 rounded-xl">
              <Building className="w-8 h-8 text-blue-500" />
            </div>
            <h1 className="text-3xl font-bold text-white">
              Car<span className="text-blue-500">Prompt</span>
            </h1>
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Garage Portal</h2>
          <p className="text-gray-400">
            {mode === "login" 
              ? "Access your analytics dashboard and manage listings" 
              : "Register your garage to start listing vehicles"}
          </p>
        </div>

        {/* Mode Tabs */}
        <div className="flex mb-6 bg-gray-900/30 rounded-xl p-1">
          <button
            onClick={() => setMode("login")}
            className={`flex-1 py-2.5 px-4 text-sm font-medium rounded-lg transition-all ${mode === "login" ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"}`}
          >
            Sign In
          </button>
          <button
            onClick={() => setMode("register")}
            className={`flex-1 py-2.5 px-4 text-sm font-medium rounded-lg transition-all ${mode === "register" ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white"}`}
          >
            Register
          </button>
        </div>

        {/* Login Card */}
        <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-2xl p-6 md:p-8 shadow-2xl">
          {/* OAuth Section */}
          <div className="mb-6">
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => handleOAuth("Google")}
                className="py-2.5 px-4 bg-gray-800/50 hover:bg-red-500/10 border border-gray-700 hover:border-red-500/50 rounded-xl text-gray-300 hover:text-red-400 font-medium transition-all flex items-center justify-center gap-2"
              >
                <Chrome className="w-4 h-4" />
                <span className="text-xs">Google</span>
              </button>
              <button
                type="button"
                onClick={() => handleOAuth("GitHub")}
                className="py-2.5 px-4 bg-gray-800/50 hover:bg-gray-800 border border-gray-700 hover:border-gray-600 rounded-xl text-gray-300 hover:text-white font-medium transition-all flex items-center justify-center gap-2"
              >
                <Github className="w-4 h-4" />
                <span className="text-xs">GitHub</span>
              </button>
              <button
                type="button"
                onClick={() => handleOAuth("Microsoft")}
                className="py-2.5 px-4 bg-gray-800/50 hover:bg-blue-500/10 border border-gray-700 hover:border-blue-500/50 rounded-xl text-gray-300 hover:text-blue-400 font-medium transition-all flex items-center justify-center gap-2"
              >
                <Square className="w-4 h-4" />
                <span className="text-xs">Microsoft</span>
              </button>
            </div>
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-800"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-gray-900/50 text-gray-500">
                  {mode === "login" ? "Or continue with email" : "Or register with email"}
                </span>
              </div>
            </div>
          </div>

          <form onSubmit={mode === "login" ? handleLoginSubmit : handleRegisterSubmit} className="space-y-6">
            {mode === "register" && (
              <>
                {/* Garage Name */}
                <div>
                  <label htmlFor="garageName" className="block text-sm font-medium text-gray-300 mb-2">
                    Garage Name
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Building className="h-5 w-5 text-gray-500" />
                    </div>
                    <input
                      id="garageName"
                      type="text"
                      value={registrationData.garageName}
                      onChange={(e) => handleRegistrationChange("garageName", e.target.value)}
                      placeholder="e.g., Pro Motors Ltd"
                      className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      required
                    />
                  </div>
                </div>

                {/* Contact Name */}
                <div>
                  <label htmlFor="contactName" className="block text-sm font-medium text-gray-300 mb-2">
                    Contact Person
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <User className="h-5 w-5 text-gray-500" />
                    </div>
                    <input
                      id="contactName"
                      type="text"
                      value={registrationData.contactName}
                      onChange={(e) => handleRegistrationChange("contactName", e.target.value)}
                      placeholder="Full name"
                      className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      required
                    />
                  </div>
                </div>
              </>
            )}

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                {mode === "login" ? "Garage Email" : "Business Email"}
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-500" />
                </div>
                <input
                  id="email"
                  type="email"
                  value={mode === "login" ? email : registrationData.email}
                  onChange={(e) => mode === "login" 
                    ? setEmail(e.target.value) 
                    : handleRegistrationChange("email", e.target.value)}
                  placeholder="your@garage.com"
                  className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-500" />
                </div>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={mode === "login" ? password : registrationData.password}
                  onChange={(e) => mode === "login" 
                    ? setPassword(e.target.value) 
                    : handleRegistrationChange("password", e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-12 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-500 hover:text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-500 hover:text-gray-400" />
                  )}
                </button>
              </div>
              
              {/* Password Strength Meter (Register only) */}
              {mode === "register" && password && (
                <div className="mt-3 space-y-3">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Password strength</span>
                    <span className={`font-medium ${getStrengthColor().replace("bg-", "text-")}`}>
                      {getStrengthLabel()}
                    </span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${getStrengthColor()} transition-all duration-300`}
                      style={{ width: `${passwordStrength}%` }}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className={`flex items-center gap-2 ${passwordCriteria.length ? 'text-green-500' : 'text-gray-500'}`}>
                      <div className={`w-3 h-3 rounded-full flex items-center justify-center ${passwordCriteria.length ? 'bg-green-500' : 'bg-gray-800'}`}>
                        {passwordCriteria.length && <Check className="w-2 h-2 text-white" />}
                      </div>
                      <span>8+ characters</span>
                    </div>
                    <div className={`flex items-center gap-2 ${passwordCriteria.uppercase ? 'text-green-500' : 'text-gray-500'}`}>
                      <div className={`w-3 h-3 rounded-full flex items-center justify-center ${passwordCriteria.uppercase ? 'bg-green-500' : 'bg-gray-800'}`}>
                        {passwordCriteria.uppercase && <Check className="w-2 h-2 text-white" />}
                      </div>
                      <span>Uppercase letter</span>
                    </div>
                    <div className={`flex items-center gap-2 ${passwordCriteria.lowercase ? 'text-green-500' : 'text-gray-500'}`}>
                      <div className={`w-3 h-3 rounded-full flex items-center justify-center ${passwordCriteria.lowercase ? 'bg-green-500' : 'bg-gray-800'}`}>
                        {passwordCriteria.lowercase && <Check className="w-2 h-2 text-white" />}
                      </div>
                      <span>Lowercase letter</span>
                    </div>
                    <div className={`flex items-center gap-2 ${passwordCriteria.number ? 'text-green-500' : 'text-gray-500'}`}>
                      <div className={`w-3 h-3 rounded-full flex items-center justify-center ${passwordCriteria.number ? 'bg-green-500' : 'bg-gray-800'}`}>
                        {passwordCriteria.number && <Check className="w-2 h-2 text-white" />}
                      </div>
                      <span>Number</span>
                    </div>
                    <div className={`flex items-center gap-2 ${passwordCriteria.special ? 'text-green-500' : 'text-gray-500'}`}>
                      <div className={`w-3 h-3 rounded-full flex items-center justify-center ${passwordCriteria.special ? 'bg-green-500' : 'bg-gray-800'}`}>
                        {passwordCriteria.special && <Check className="w-2 h-2 text-white" />}
                      </div>
                      <span>Special character</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password (Register only) */}
            {mode === "register" && (
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-500" />
                  </div>
                  <input
                    id="confirmPassword"
                    type="password"
                    value={registrationData.confirmPassword}
                    onChange={(e) => handleRegistrationChange("confirmPassword", e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                    required
                  />
                </div>
                {registrationData.confirmPassword && registrationData.password !== registrationData.confirmPassword && (
                  <p className="mt-1 text-xs text-red-500">Passwords do not match</p>
                )}
              </div>
            )}

            {/* Phone & Address (Register only) */}
            {mode === "register" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Phone className="h-5 w-5 text-gray-500" />
                    </div>
                    <input
                      id="phone"
                      type="tel"
                      value={registrationData.phone}
                      onChange={(e) => handleRegistrationChange("phone", e.target.value)}
                      placeholder="+44 123 456 7890"
                      className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="address" className="block text-sm font-medium text-gray-300 mb-2">
                    Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <MapPin className="h-5 w-5 text-gray-500" />
                    </div>
                    <input
                      id="address"
                      type="text"
                      value={registrationData.address}
                      onChange={(e) => handleRegistrationChange("address", e.target.value)}
                      placeholder="City, Postcode"
                      className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      required
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Remember Me & Forgot Password (Login only) */}
            {mode === "login" && (
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="h-4 w-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500 focus:ring-offset-gray-900"
                  />
                  <label htmlFor="remember-me" className="ml-2 text-sm text-gray-400">
                    Remember me
                  </label>
                </div>
                <button
                  type="button"
                  className="text-sm text-blue-500 hover:text-blue-400 transition-colors"
                  onClick={() => alert("Password reset functionality coming soon")}
                >
                  Forgot password?
                </button>
              </div>
            )}

            {/* Terms Agreement (Register only) */}
            {mode === "register" && (
              <div className="flex items-start">
                <input
                  id="terms"
                  type="checkbox"
                  required
                  className="h-4 w-4 mt-1 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500 focus:ring-offset-gray-900"
                />
                <label htmlFor="terms" className="ml-2 text-sm text-gray-400">
                  I agree to the{" "}
                  <button type="button" className="text-blue-500 hover:text-blue-400" onClick={() => alert("Terms coming soon")}>
                    Terms of Service
                  </button>{" "}
                  and{" "}
                  <button type="button" className="text-blue-500 hover:text-blue-400" onClick={() => alert("Privacy policy coming soon")}>
                    Privacy Policy
                  </button>
                  . I understand my garage will be verified before going live.
                </label>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 px-4 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {mode === "login" ? "Signing in..." : "Creating account..."}
                </>
              ) : (
                <>
                  <Car className="w-5 h-5" />
                  {mode === "login" ? "Sign in to Garage Portal" : "Register Garage"}
                </>
              )}
            </button>

            {/* Mode Switch */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => setMode(mode === "login" ? "register" : "login")}
                className="text-sm text-blue-500 hover:text-blue-400 transition-colors"
              >
                {mode === "login" 
                  ? "Don't have an account? Register your garage" 
                  : "Already have an account? Sign in"}
              </button>
            </div>
          </form>

          {/* Security Notice */}
          <div className="mt-6 pt-6 border-t border-gray-800">
            <p className="text-xs text-gray-500 text-center">
              Your data is secured with industry-standard encryption.{" "}
              {mode === "login" && "By signing in, you agree to our "}
              {mode === "login" && (
                <>
                  <button className="text-blue-500 hover:text-blue-400" onClick={() => alert("Terms coming soon")}>
                    Terms of Service
                  </button>{" "}
                  and{" "}
                  <button className="text-blue-500 hover:text-blue-400" onClick={() => alert("Privacy policy coming soon")}>
                    Privacy Policy
                  </button>
                  .
                </>
              )}
              {mode === "register" && "All garage registrations are manually verified within 24-48 hours."}
            </p>
          </div>
        </div>

        {/* Stats Footer */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          <div className="p-4 bg-gray-900/30 rounded-xl">
            <div className="text-2xl font-bold text-white">500+</div>
            <div className="text-xs text-gray-400">Garages</div>
          </div>
          <div className="p-4 bg-gray-900/30 rounded-xl">
            <div className="text-2xl font-bold text-white">10k+</div>
            <div className="text-xs text-gray-400">Listings</div>
          </div>
          <div className="p-4 bg-gray-900/30 rounded-xl">
            <div className="text-2xl font-bold text-white">24/7</div>
            <div className="text-xs text-gray-400">Support</div>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-8 text-center">
          <button
            onClick={() => router.push("/")}
            className="text-gray-500 hover:text-gray-400 text-sm transition-colors"
          >
            ← Back to car search
          </button>
        </div>
      </div>
    </main>
  );
}