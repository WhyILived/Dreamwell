"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Users, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    companyName: "",
    website: "",
    email: "",
    password: "",
    confirmPassword: "",
    keywords: "",
  })
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  
  const { register } = useAuth()
  const router = useRouter()

  const validateForm = () => {
    const errors: {[key: string]: string} = {}
    
    // Company name validation
    if (!formData.companyName.trim()) {
      errors.companyName = "Company name is required"
    }
    
    // Website validation
    if (!formData.website.trim()) {
      errors.website = "Website URL is required"
    } else {
      const websiteRegex = /^https?:\/\/.+\..+/
      if (!websiteRegex.test(formData.website)) {
        errors.website = "Please enter a valid website URL (e.g., https://yourcompany.com)"
      }
    }
    
    // Email validation
    if (!formData.email.trim()) {
      errors.email = "Email is required fuck you code"
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(formData.email)) {
        errors.email = "Please enter a valid email address"
      }
    }
    
    // Password validation
    if (!formData.password) {
      errors.password = "Password is required"
    } else if (formData.password.length < 8) {
      errors.password = "Password must be at least 8 characters long"
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = "Password must contain at least one uppercase letter, one lowercase letter, and one number"
    }
    
    // Confirm password validation
    if (!formData.confirmPassword) {
      errors.confirmPassword = "Please confirm your password"
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = "Passwords do not match"
    }
    
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")
    setValidationErrors({})
    
    // Validate form
    if (!validateForm()) {
      setIsLoading(false)
      return
    }
    
    try {
      await register({
        email: formData.email,
        password: formData.password,
        company_name: formData.companyName,
        website: formData.website,
        keywords: formData.keywords,
      })
      router.push("/dashboard")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Link href="/" className="flex items-center text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">Dreamwell</span>
          </div>
        </div>

        <Card className="border-border">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Create Your Company Account</CardTitle>
            <CardDescription>
              Join Dreamwell to start connecting with the perfect influencers for your brand. We'll analyze your website to understand your brand better.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="companyName">Company Name *</Label>
                  <Input
                    id="companyName"
                    name="companyName"
                    value={formData.companyName}
                    onChange={handleChange}
                    placeholder="Your Company Inc."
                    className={validationErrors.companyName ? "border-red-500" : ""}
                    required
                  />
                  {validationErrors.companyName && (
                    <p className="text-sm text-red-500">{validationErrors.companyName}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="website">Website URL *</Label>
                  <Input
                    id="website"
                    name="website"
                    type="url"
                    value={formData.website}
                    onChange={handleChange}
                    placeholder="https://yourcompany.com"
                    className={validationErrors.website ? "border-red-500" : ""}
                    required
                  />
                  {validationErrors.website && (
                    <p className="text-sm text-red-500">{validationErrors.website}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Business Email *</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@yourcompany.com"
                  className={validationErrors.email ? "border-red-500" : ""}
                  required
                />
                {validationErrors.email && (
                  <p className="text-sm text-red-500">{validationErrors.email}</p>
                )}
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Create a strong password"
                    className={validationErrors.password ? "border-red-500" : ""}
                    required
                  />
                  {validationErrors.password && (
                    <p className="text-sm text-red-500">{validationErrors.password}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password *</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="Confirm your password"
                    className={validationErrors.confirmPassword ? "border-red-500" : ""}
                    required
                  />
                  {validationErrors.confirmPassword && (
                    <p className="text-sm text-red-500">{validationErrors.confirmPassword}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="keywords">Company Keywords</Label>
                <Textarea
                  id="keywords"
                  name="keywords"
                  value={formData.keywords}
                  onChange={handleChange}
                  placeholder="Enter keywords that describe your brand, products, or services (e.g., sustainable fashion, tech gadgets, organic skincare)..."
                  rows={4}
                />
              </div>

              {error && (
                <div className="text-sm text-red-500 text-center">
                  {error}
                </div>
              )}

              <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
                {isLoading ? "Creating Account..." : "Create Account & Analyze Brand"}
              </Button>

              <div className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link href="/login" className="text-accent hover:underline">
                  Sign in here
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
