import { useState, useEffect } from "react";
import {
    User,
    Mail,
    Shield,
    Lock,
    Eye,
    EyeOff,
    Save,
    LogOut,
    KeyRound,
    CheckCircle2,
    AlertTriangle,
    Clock,
    Fingerprint,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { updateProfile, changePassword } from "../lib/api";
import { useNavigate } from "react-router-dom";

const ROLE_COLORS: Record<string, string> = {
    admin: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    viewer: "bg-gray-500/15 text-gray-400 border-gray-500/30",
    analyst: "bg-purple-500/15 text-purple-400 border-purple-500/30",
};

export function AdminProfile() {
    const { user, logout, refreshUser } = useAuth();
    const { success, error } = useToast();
    const navigate = useNavigate();

    // Profile form state
    const [username, setUsername] = useState(user?.username ?? "");
    const [email, setEmail] = useState(user?.email ?? "");
    const [savingProfile, setSavingProfile] = useState(false);

    // Password form state
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showCurrent, setShowCurrent] = useState(false);
    const [showNew, setShowNew] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);
    const [savingPassword, setSavingPassword] = useState(false);

    // Sync form when user context loads
    useEffect(() => {
        if (user) {
            setUsername(user.username);
            setEmail(user.email);
        }
    }, [user]);

    const sessionToken = localStorage.getItem("prism_token");
    const tokenPreview = sessionToken
        ? `${sessionToken.slice(0, 20)}...${sessionToken.slice(-8)}`
        : "—";

    // Password strength
    const passwordStrength = (p: string) => {
        if (!p) return { label: "", color: "", width: "0%" };
        if (p.length < 6) return { label: "Too short", color: "bg-red-500", width: "20%" };
        if (p.length < 8) return { label: "Weak", color: "bg-orange-500", width: "40%" };
        if (!/[A-Z]/.test(p) || !/[0-9]/.test(p)) return { label: "Fair", color: "bg-yellow-500", width: "60%" };
        if (p.length >= 12) return { label: "Strong", color: "bg-emerald-500", width: "100%" };
        return { label: "Good", color: "bg-blue-500", width: "80%" };
    };

    const strength = passwordStrength(newPassword);

    const handleSaveProfile = async () => {
        if (!username.trim()) { error("Username cannot be empty"); return; }
        if (!email.trim()) { error("Email cannot be empty"); return; }
        setSavingProfile(true);
        try {
            await updateProfile({ username: username.trim(), email: email.trim() });
            await refreshUser();
            success("Profile updated successfully!");
        } catch (err: unknown) {
            error(err instanceof Error ? err.message : "Failed to update profile");
        } finally {
            setSavingProfile(false);
        }
    };

    const handleChangePassword = async () => {
        if (!currentPassword) { error("Current password is required"); return; }
        if (newPassword.length < 6) { error("New password must be at least 6 characters"); return; }
        if (newPassword !== confirmPassword) { error("New passwords do not match"); return; }
        setSavingPassword(true);
        try {
            await changePassword({ current_password: currentPassword, new_password: newPassword });
            success("Password changed successfully!");
            setCurrentPassword("");
            setNewPassword("");
            setConfirmPassword("");
        } catch (err: unknown) {
            error(err instanceof Error ? err.message : "Failed to change password");
        } finally {
            setSavingPassword(false);
        }
    };

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    const roleColor = ROLE_COLORS[user?.role ?? "viewer"] ?? ROLE_COLORS.viewer;
    const initials = (user?.username ?? "?")[0].toUpperCase();

    return (
        <div className="space-y-8 max-w-3xl mx-auto xl:mx-0">
            {/* Page Header */}
            <div>
                <h1 className="text-2xl font-bold text-white mb-1">Admin Profile</h1>
                <p className="text-gray-400">Manage your account credentials and platform access.</p>
            </div>

            {/* ── Section 1: Account Overview ── */}
            <div className="glass-card p-6 sm:p-8 border border-white/5 rounded-xl">
                <div className="flex items-center gap-3 mb-6 pb-5 border-b border-white/10">
                    <div className="p-2.5 rounded-lg bg-blue-500/10">
                        <User className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                        <h2 className="text-base font-semibold text-white">Account Overview</h2>
                        <p className="text-xs text-gray-500">Your current account snapshot</p>
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                    {/* Avatar */}
                    <div className="relative shrink-0">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500/30 to-indigo-600/30 border border-blue-500/20 flex items-center justify-center text-3xl font-bold text-blue-300 ring-4 ring-blue-500/10 shadow-lg shadow-blue-900/20">
                            {initials}
                        </div>
                        <div className="absolute -bottom-1.5 -right-1.5 w-5 h-5 bg-emerald-500 rounded-full border-2 border-[#0f172a] flex items-center justify-center">
                            <CheckCircle2 className="w-3 h-3 text-white" />
                        </div>
                    </div>

                    {/* Info grid */}
                    <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
                        <InfoRow icon={<User className="w-4 h-4 text-blue-400" />} label="Username" value={user?.username ?? "—"} />
                        <InfoRow icon={<Mail className="w-4 h-4 text-indigo-400" />} label="Email" value={user?.email ?? "—"} />
                        <div className="flex flex-col gap-1">
                            <span className="text-[11px] text-gray-500 uppercase tracking-wide flex items-center gap-1.5">
                                <Shield className="w-3.5 h-3.5" /> Role
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border w-fit uppercase tracking-wider ${roleColor}`}>
                                {user?.role ?? "viewer"}
                            </span>
                        </div>
                        <InfoRow icon={<Fingerprint className="w-4 h-4 text-purple-400" />} label="User ID" value={user?.id ? `#${user.id.slice(-8)}` : "—"} mono />
                    </div>
                </div>
            </div>

            {/* ── Section 2: Edit Profile ── */}
            <div className="glass-card p-6 sm:p-8 border border-white/5 rounded-xl">
                <div className="flex items-center gap-3 mb-6 pb-5 border-b border-white/10">
                    <div className="p-2.5 rounded-lg bg-indigo-500/10">
                        <Mail className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div>
                        <h2 className="text-base font-semibold text-white">Profile Information</h2>
                        <p className="text-xs text-gray-500">Update your username and email address</p>
                    </div>
                </div>

                <div className="space-y-5">
                    <FormField label="Username" icon={<User className="w-4 h-4 text-blue-400" />}>
                        <input
                            id="profile-username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="your_username"
                            className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50 transition-all placeholder:text-gray-600"
                        />
                    </FormField>

                    <FormField label="Email Address" icon={<Mail className="w-4 h-4 text-indigo-400" />}>
                        <input
                            id="profile-email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="admin@prism.org"
                            className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3.5 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/40 focus:border-indigo-500/50 transition-all placeholder:text-gray-600"
                        />
                    </FormField>

                    <div className="pt-2 flex justify-end">
                        <button
                            id="save-profile-btn"
                            onClick={handleSaveProfile}
                            disabled={savingProfile}
                            className="flex items-center gap-2 px-8 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-all shadow-lg shadow-blue-900/20 w-full sm:w-auto justify-center"
                        >
                            {savingProfile ? (
                                <div className="animate-spin w-5 h-5 border-2 border-white/30 border-t-white rounded-full" />
                            ) : (
                                <Save className="w-5 h-5" />
                            )}
                            Save Profile
                        </button>
                    </div>
                </div>
            </div>

            {/* ── Section 3: Change Password ── */}
            <div className="glass-card p-6 sm:p-8 border border-white/5 rounded-xl">
                <div className="flex items-center gap-3 mb-6 pb-5 border-b border-white/10">
                    <div className="p-2.5 rounded-lg bg-emerald-500/10">
                        <KeyRound className="w-5 h-5 text-emerald-400" />
                    </div>
                    <div>
                        <h2 className="text-base font-semibold text-white">Security — Change Password</h2>
                        <p className="text-xs text-gray-500">Use a strong password you don't use elsewhere</p>
                    </div>
                </div>

                <div className="space-y-5">
                    <FormField label="Current Password" icon={<Lock className="w-4 h-4 text-gray-400" />}>
                        <PasswordInput
                            id="current-password"
                            value={currentPassword}
                            onChange={setCurrentPassword}
                            show={showCurrent}
                            onToggle={() => setShowCurrent(!showCurrent)}
                            placeholder="Enter current password"
                        />
                    </FormField>

                    <FormField label="New Password" icon={<Lock className="w-4 h-4 text-emerald-400" />}>
                        <PasswordInput
                            id="new-password"
                            value={newPassword}
                            onChange={setNewPassword}
                            show={showNew}
                            onToggle={() => setShowNew(!showNew)}
                            placeholder="Enter new password"
                        />
                        {newPassword && (
                            <div className="mt-2 space-y-1">
                                <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${strength.color}`}
                                        style={{ width: strength.width }}
                                    />
                                </div>
                                <p className={`text-xs ${strength.color.replace("bg-", "text-")}`}>{strength.label}</p>
                            </div>
                        )}
                    </FormField>

                    <FormField label="Confirm New Password" icon={<Lock className="w-4 h-4 text-emerald-400" />}>
                        <PasswordInput
                            id="confirm-password"
                            value={confirmPassword}
                            onChange={setConfirmPassword}
                            show={showConfirm}
                            onToggle={() => setShowConfirm(!showConfirm)}
                            placeholder="Re-enter new password"
                        />
                        {confirmPassword && newPassword !== confirmPassword && (
                            <p className="text-xs text-red-400 mt-1.5 flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" /> Passwords do not match
                            </p>
                        )}
                        {confirmPassword && newPassword === confirmPassword && newPassword.length >= 6 && (
                            <p className="text-xs text-emerald-400 mt-1.5 flex items-center gap-1">
                                <CheckCircle2 className="w-3 h-3" /> Passwords match
                            </p>
                        )}
                    </FormField>

                    <div className="pt-2 flex justify-end">
                        <button
                            id="change-password-btn"
                            onClick={handleChangePassword}
                            disabled={savingPassword}
                            className="flex items-center gap-2 px-8 py-3 bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-all shadow-lg shadow-emerald-900/20 w-full sm:w-auto justify-center"
                        >
                            {savingPassword ? (
                                <div className="animate-spin w-5 h-5 border-2 border-white/30 border-t-white rounded-full" />
                            ) : (
                                <KeyRound className="w-5 h-5" />
                            )}
                            Change Password
                        </button>
                    </div>
                </div>
            </div>

            {/* ── Section 4: Session & Danger Zone ── */}
            <div className="glass-card p-6 sm:p-8 border border-white/5 rounded-xl">
                <div className="flex items-center gap-3 mb-6 pb-5 border-b border-white/10">
                    <div className="p-2.5 rounded-lg bg-yellow-500/10">
                        <Clock className="w-5 h-5 text-yellow-400" />
                    </div>
                    <div>
                        <h2 className="text-base font-semibold text-white">Session & Access</h2>
                        <p className="text-xs text-gray-500">Current session details and sign-out</p>
                    </div>
                </div>

                <div className="space-y-5">
                    {/* Token display */}
                    <div className="rounded-lg bg-black/30 border border-white/10 p-4 space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Active Session Token</span>
                            <span className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-semibold rounded-full uppercase tracking-wider">Live</span>
                        </div>
                        <code className="block text-xs text-gray-500 font-mono break-all">{tokenPreview}</code>
                    </div>

                    {/* Sign Out */}
                    <div className="rounded-lg border border-red-500/20 bg-red-500/5 p-4">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                            <div>
                                <p className="text-sm font-semibold text-red-300">Sign Out</p>
                                <p className="text-xs text-red-400/70 mt-0.5">Ends your current session and redirects to login.</p>
                            </div>
                            <button
                                id="sign-out-btn"
                                onClick={handleLogout}
                                className="flex items-center gap-2 px-6 py-2.5 bg-red-600/20 hover:bg-red-600/40 border border-red-500/30 text-red-400 hover:text-red-300 rounded-lg text-sm font-medium transition-all shrink-0 justify-center"
                            >
                                <LogOut className="w-4 h-4" />
                                Sign Out
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ── Helper sub-components ── */

function InfoRow({
    icon, label, value, mono = false,
}: {
    icon: React.ReactNode; label: string; value: string; mono?: boolean;
}) {
    return (
        <div className="flex flex-col gap-1">
            <span className="text-[11px] text-gray-500 uppercase tracking-wide flex items-center gap-1.5">{icon} {label}</span>
            <span className={`text-sm text-white font-medium truncate ${mono ? "font-mono" : ""}`}>{value}</span>
        </div>
    );
}

function FormField({
    label, icon, children,
}: {
    label: string; icon: React.ReactNode; children: React.ReactNode;
}) {
    return (
        <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-300 flex items-center gap-2 uppercase tracking-wide">
                {icon} {label}
            </label>
            {children}
        </div>
    );
}

function PasswordInput({
    id, value, onChange, show, onToggle, placeholder,
}: {
    id: string; value: string; onChange: (v: string) => void;
    show: boolean; onToggle: () => void; placeholder: string;
}) {
    return (
        <div className="relative">
            <input
                id={id}
                type={show ? "text" : "password"}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3.5 pr-12 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500/50 transition-all placeholder:text-gray-600"
            />
            <button
                type="button"
                onClick={onToggle}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-300 transition-colors"
            >
                {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
        </div>
    );
}
