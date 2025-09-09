"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Users, Building2, Menu, Settings, LogOut, Package, Search } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const navigation = [
  { name: "Brand Profile", href: "/dashboard", icon: Building2 },
  { name: "Products", href: "/dashboard/products", icon: Package },
  { name: "Influencers", href: "/dashboard/influencers", icon: Search },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const pathname = usePathname()

  const Sidebar = ({ className }: { className?: string }) => (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Logo */}
      <div className="flex items-center space-x-2 p-6 border-b border-sidebar-border">
        <div className="w-8 h-8 bg-sidebar-accent rounded-lg flex items-center justify-center">
          <Users className="w-5 h-5 text-sidebar-accent-foreground" />
        </div>
        <span className="text-xl font-bold text-sidebar-foreground">InfluenceHub</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-primary hover:text-sidebar-primary-foreground",
              )}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border space-y-2">
        <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-primary">
          <Settings className="w-4 h-4 mr-3" />
          Settings
        </Button>
        <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-primary">
          <LogOut className="w-4 h-4 mr-3" />
          Sign Out
        </Button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:bg-sidebar lg:border-r lg:border-sidebar-border">
        <Sidebar />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetTrigger asChild className="lg:hidden">
          <Button variant="ghost" size="icon" className="fixed top-4 left-4 z-50">
            <Menu className="w-5 h-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0 bg-sidebar">
          <Sidebar />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
