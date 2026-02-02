
export default function NavBar() {
    return (
        <nav class="flex justify-end border-b border-gray-700 bg-grey-900">
            <ul class="flex justify-end h-12 max-w-5xl items-center gap-6 px-4 text-sm">
                <li>
                    <a
                        href="/"
                        aria-current="page"
                        class="nav-link"
                    >
                        Home
                    </a>
                </li>
                <li>
                    <a href="/account" class="nav-link">
                        Account
                    </a>
                </li>
                <li>
                    <a href="/logout" class="nav-link">
                        Logout
                    </a>
                </li>
            </ul>
        </nav>
)
    ;
}
